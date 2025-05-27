from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Union
import sqlalchemy
from sqlalchemy.engine import RowMapping
from dataclasses import dataclass
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)


class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int = Field(gt=0, description="Must be greater than 0")
    potion_type: List[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d] that sum to 1.0",
    )
    price: int = Field(ge=0, description="Price must be non-negative")
    quantity: int = Field(ge=0, description="Quantity must be non-negative")

    @field_validator("potion_type")
    @classmethod
    def validate_potion_type(cls, potion_type: List[float]) -> List[float]:
        if len(potion_type) != 4:
            raise ValueError("potion_type must have exactly 4 elements: [r, g, b, d]")
        if not abs(sum(potion_type) - 1.0) < 1e-6:
            raise ValueError("Sum of potion_type values must be exactly 1.0")
        return potion_type


class BarrelOrder(BaseModel):
    sku: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")


@dataclass
class BarrelSummary:
    gold_paid: int


def calculate_barrel_summary(barrels: List[Barrel]) -> BarrelSummary:
    return BarrelSummary(gold_paid=sum(b.price * b.quantity for b in barrels))


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_barrels(barrels_delivered: List[Barrel], order_id: str):
    with db.engine.begin() as connection:
        # check if the order_id was already processed
        already = connection.execute(
            sqlalchemy.text("""
                SELECT 1 FROM processed_requests WHERE order_id = :order_id
            """),
            {"order_id": order_id},
        ).first()

        if already:
            print(f"Skipping order {order_id} (already processed)")
            return

        # it's safe to insert
        connection.execute(
            sqlalchemy.text("""
                INSERT INTO processed_requests (order_id)
                VALUES (:order_id)
            """),
            {"order_id": order_id},
        )

        gold: int = (
            connection.execute(
                sqlalchemy.text("SELECT amount FROM gold_inventory")
            ).scalar()
            or 0
        )

        total_cost = sum(b.price * b.quantity for b in barrels_delivered)
        if gold < total_cost:
            print(f"[SKIPPED] Not enough gold ({gold}) for total cost {total_cost}")
            return

        ml_updates = {
            "red_ml": 0,
            "green_ml": 0,
            "blue_ml": 0,
            "dark_ml": 0,
        }

        for barrel in barrels_delivered:
            total_ml = barrel.ml_per_barrel * barrel.quantity
            for ratio, color in zip(barrel.potion_type, ml_updates):
                added = int(ratio * total_ml)
                ml_updates[color] += added

        print("[DEBUG] ML Updates:", ml_updates)
        print("[DEBUG] Total Cost:", total_cost)

        # update liquid ledger
        for color, amount in ml_updates.items():
            if amount > 0:
                connection.execute(
                    sqlalchemy.text("""
                        INSERT INTO ledger_entries (category, sub_type, quantity, order_id, source)
                        VALUES ('liquid', :sub_type, :quantity, :order_id, 'barrels')
                    """),
                    {"sub_type": color, "quantity": amount, "order_id": order_id},
                )

        # update liquid_inventory
        connection.execute(
            sqlalchemy.text("""
                UPDATE liquid_inventory
                SET red_ml = red_ml + :r,
                    green_ml = green_ml + :g,
                    blue_ml = blue_ml + :b,
                    dark_ml = dark_ml + :d
                WHERE id = 1
            """),
            {
                "r": ml_updates["red_ml"],
                "g": ml_updates["green_ml"],
                "b": ml_updates["blue_ml"],
                "d": ml_updates["dark_ml"],
            },
        )

        # log and deduct gold
        connection.execute(
            sqlalchemy.text("""
                INSERT INTO ledger_entries (category, quantity, order_id, source)
                VALUES ('gold', :amount, :order_id, 'barrels')
            """),
            {"amount": -total_cost, "order_id": order_id},
        )

        connection.execute(
            sqlalchemy.text("""
                UPDATE gold_inventory
                SET amount = amount - :cost
            """),
            {"cost": total_cost},
        )

        print(f"[SUCCESS] Delivered barrels for order {order_id}")


def create_barrel_plan(
    gold: int,
    max_barrel_capacity: int,
    current_red_ml: int,
    current_green_ml: int,
    current_blue_ml: int,
    current_dark_ml: int,
    wholesale_catalog: List[Barrel],
) -> List[BarrelOrder]:
    LOW_THRESHOLD = 50  # only consider buying if a color is below this
    MIN_ML_PER_GOLD = 1.0  # avoid barrels that give less than this much ml per gold
    color_index = {"red": 0, "green": 1, "blue": 2, "dark": 3}
    color_stock = {
        "red": current_red_ml or 0,
        "green": current_green_ml or 0,
        "blue": current_blue_ml or 0,
        "dark": current_dark_ml or 0,
    }

    low_colors = [
        (color, amount)
        for color, amount in color_stock.items()
        if amount < LOW_THRESHOLD
    ]
    if not low_colors:
        return []

    lowest_color = min(low_colors, key=lambda x: x[1])[0]
    idx = color_index[lowest_color]

    pure_barrels = []
    for b in wholesale_catalog:
        is_pure = b.potion_type[idx] == 1.0 and sum(b.potion_type) == 1.0
        if is_pure and b.price <= gold:
            ml_per_gold = b.ml_per_barrel / b.price if b.price > 0 else float("inf")
            if ml_per_gold >= MIN_ML_PER_GOLD:
                pure_barrels.append((b, ml_per_gold))

    if not pure_barrels:
        return []

    best_barrel = max(pure_barrels, key=lambda x: x[1])[0]
    return [BarrelOrder(sku=best_barrel.sku, quantity=1)]


@router.post("/plan", response_model=List[BarrelOrder])
def get_wholesale_purchase_plan(wholesale_catalog: List[Barrel]):
    with db.engine.begin() as connection:
        gold: int = (
            connection.execute(
                sqlalchemy.text("SELECT amount FROM gold_inventory")
            ).scalar()
            or 0
        )

        result: Union[RowMapping, dict[str, int]] = (
            connection.execute(
                sqlalchemy.text("""
                    SELECT
                        SUM(CASE WHEN sub_type = 'red_ml' THEN quantity ELSE 0 END) AS red_ml,
                        SUM(CASE WHEN sub_type = 'green_ml' THEN quantity ELSE 0 END) AS green_ml,
                        SUM(CASE WHEN sub_type = 'blue_ml' THEN quantity ELSE 0 END) AS blue_ml,
                        SUM(CASE WHEN sub_type = 'dark_ml' THEN quantity ELSE 0 END) AS dark_ml
                    FROM ledger_entries
                    WHERE category = 'liquid'
                """)
            )
            .mappings()
            .first()
            or {}
        )

        ml_result: dict[str, int] = {
            "red_ml": result.get("red_ml", 0),
            "green_ml": result.get("green_ml", 0),
            "blue_ml": result.get("blue_ml", 0),
            "dark_ml": result.get("dark_ml", 0),
        }

        return create_barrel_plan(
            gold=gold,
            max_barrel_capacity=10000,
            current_red_ml=ml_result["red_ml"],
            current_green_ml=ml_result["green_ml"],
            current_blue_ml=ml_result["blue_ml"],
            current_dark_ml=ml_result["dark_ml"],
            wholesale_catalog=wholesale_catalog,
        )
