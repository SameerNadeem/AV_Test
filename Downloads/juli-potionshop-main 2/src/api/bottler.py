from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


class PotionMixes(BaseModel):
    potion_type: List[int] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain [r, g, b, d] summing to 100",
    )
    quantity: int = Field(..., ge=1, le=10000)

    @field_validator("potion_type")
    @classmethod
    def validate_mix(cls, potion_type: List[int]) -> List[int]:
        if sum(potion_type) != 100:
            raise ValueError("Sum of potion_type must be 100")
        return potion_type


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_bottles(potions_delivered: List[PotionMixes], order_id: str):
    with db.engine.begin() as connection:
        try:
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO processed_requests (order_id) VALUES (:order_id)"
                ),
                {"order_id": order_id},
            )
        except sqlalchemy.exc.IntegrityError:
            return  # Already processed

        # Get available liquid
        result = (
            connection.execute(
                sqlalchemy.text("""
                SELECT
                    red_ml, green_ml, blue_ml, dark_ml
                FROM liquid_inventory
                WHERE TRUE
            """)
            )
            .mappings()
            .first()
        )

        liquid = {k: (v if v is not None else 0) for k, v in (result or {}).items()}

        for potion in potions_delivered:
            r, g, b, d = potion.potion_type
            qty = potion.quantity
            red_ml, green_ml, blue_ml, dark_ml = r * qty, g * qty, b * qty, d * qty

            recipe = (
                connection.execute(
                    sqlalchemy.text("""
                    SELECT sku, r, g, b, d, price, name, active
                    FROM potion_catalog
                    WHERE r = :r AND g = :g AND b = :b AND d = :d
                    LIMIT 1
                """),
                    {"r": r, "g": g, "b": b, "d": d},
                )
                .mappings()
                .first()
            )

            if not recipe:
                print(f"Skipping: No matching recipe for potion {r, g, b, d}")
                continue

            if (
                liquid["red_ml"] < red_ml
                or liquid["green_ml"] < green_ml
                or liquid["blue_ml"] < blue_ml
                or liquid["dark_ml"] < dark_ml
            ):
                print(f"Skipping: Not enough liquid for potion {r, g, b, d}")
                continue

            # Deduct liquid in ledger
            for color, used in zip(
                ["red_ml", "green_ml", "blue_ml", "dark_ml"],
                [red_ml, green_ml, blue_ml, dark_ml],
            ):
                if used > 0:
                    connection.execute(
                        sqlalchemy.text("""
                            INSERT INTO ledger_entries (category, sub_type, quantity, order_id, source)
                            VALUES ('liquid', :sub_type, :quantity, :order_id, 'bottler')
                        """),
                        {"sub_type": color, "quantity": -used, "order_id": order_id},
                    )

            # Deduct liquid in inventory
            connection.execute(
                sqlalchemy.text("""
                    UPDATE liquid_inventory
                    SET red_ml = red_ml - :r,
                        green_ml = green_ml - :g,
                        blue_ml = blue_ml - :b,
                        dark_ml = dark_ml - :d
                """),
                {"r": red_ml, "g": green_ml, "b": blue_ml, "d": dark_ml},
            )

            # Insert potion into ledger
            connection.execute(
                sqlalchemy.text("""
                    INSERT INTO ledger_entries (category, sub_type, quantity, order_id, source)
                    VALUES ('potion', :sku, :qty, :order_id, 'bottler')
                """),
                {"sku": recipe["sku"], "qty": qty, "order_id": order_id},
            )

            # Ensure potion exists in potions table
            connection.execute(
                sqlalchemy.text("""
                    INSERT INTO potions (sku, name, price, quantity, r, g, b, d, active)
                    VALUES (:sku, :name, :price, 0, :r, :g, :b, :d, :active)
                    ON CONFLICT (sku) DO NOTHING
                """),
                {
                    "sku": recipe["sku"],
                    "name": recipe["name"],
                    "price": recipe["price"],
                    "r": recipe["r"],
                    "g": recipe["g"],
                    "b": recipe["b"],
                    "d": recipe["d"],
                    "active": recipe["active"],
                },
            )

            # Update potion count
            connection.execute(
                sqlalchemy.text("""
                    UPDATE potions
                    SET quantity = quantity + :qty
                    WHERE sku = :sku
                """),
                {"qty": qty, "sku": recipe["sku"]},
            )

            # Update inventory table
            connection.execute(
                sqlalchemy.text("""
                    INSERT INTO potion_inventory (sku, quantity)
                    VALUES (:sku, :qty)
                    ON CONFLICT (sku) DO UPDATE
                    SET quantity = potion_inventory.quantity + :qty
                """),
                {"sku": recipe["sku"], "qty": qty},
            )


@router.post("/plan", response_model=List[PotionMixes])
def get_bottle_plan():
    with db.engine.begin() as connection:
        result = (
            connection.execute(
                sqlalchemy.text("""
                SELECT red_ml, green_ml, blue_ml, dark_ml
                FROM liquid_inventory
                WHERE TRUE
                """)
            )
            .mappings()
            .first()
        )

        liquid = {k: (v if v is not None else 0) for k, v in (result or {}).items()}

        current_potion_count = (
            connection.execute(
                sqlalchemy.text("""
                SELECT SUM(quantity) FROM ledger_entries WHERE category = 'potion'
                """)
            ).scalar()
            or 0
        )

        potions = connection.execute(
            sqlalchemy.text("SELECT r, g, b, d, price FROM potion_catalog")
        ).fetchall()

        catalog = [(p.r, p.g, p.b, p.d, p.price) for p in potions]

    return create_bottle_plan(
        red_ml=liquid.get("red_ml", 0),
        green_ml=liquid.get("green_ml", 0),
        blue_ml=liquid.get("blue_ml", 0),
        dark_ml=liquid.get("dark_ml", 0),
        maximum_potion_capacity=5000,
        current_potion_count=current_potion_count,
        potion_catalog=catalog,
    )


def create_bottle_plan(
    red_ml: int,
    green_ml: int,
    blue_ml: int,
    dark_ml: int,
    maximum_potion_capacity: int,
    current_potion_count: int,
    potion_catalog: List[tuple[int, int, int, int, int]],
) -> List[PotionMixes]:
    print(f"red_ml: {red_ml}, potion_catalog: {potion_catalog}")
    plan = []
    available = {
        k: int(v) if v is not None else 0
        for k, v in {"r": red_ml, "g": green_ml, "b": blue_ml, "d": dark_ml}.items()
    }

    sorted_potions = sorted(
        potion_catalog, key=lambda p: (-sum(1 for x in p[:4] if x > 0), p[4])
    )

    max_additional_potions = maximum_potion_capacity - current_potion_count
    if max_additional_potions <= 0:
        return []

    for r, g, b, d, price in sorted_potions:
        if r + g + b + d == 0:
            continue

        quantity = int(
            min(
                available["r"] // r if r else float("inf"),
                available["g"] // g if g else float("inf"),
                available["b"] // b if b else float("inf"),
                available["d"] // d if d else float("inf"),
                max_additional_potions,
            )
        )

        if quantity > 0:
            plan.append(PotionMixes(potion_type=[r, g, b, d], quantity=quantity))
            available["r"] -= int(r * quantity)
            available["g"] -= int(g * quantity)
            available["b"] -= int(b * quantity)
            available["d"] -= int(d * quantity)
            max_additional_potions -= quantity

    return plan


if __name__ == "__main__":
    print(get_bottle_plan())
