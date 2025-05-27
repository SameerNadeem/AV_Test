from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)


class InventoryAudit(BaseModel):
    number_of_potions: int
    ml_in_barrels: int
    gold: int


class CapacityPlan(BaseModel):
    potion_capacity: int = Field(
        ge=0, le=10, description="Potion capacity units, max 10"
    )
    ml_capacity: int = Field(ge=0, le=10, description="ML capacity units, max 10")


@router.get("/audit", response_model=InventoryAudit)
def get_inventory():
    try:
        with db.engine.begin() as connection:
            # Liquid ML totals
            liquid = (
                connection.execute(
                    sqlalchemy.text(
                        "SELECT red_ml, green_ml, blue_ml, dark_ml FROM liquid_inventory LIMIT 1"
                    )
                )
                .mappings()
                .first()
            )
            if not liquid:
                raise HTTPException(
                    status_code=500, detail="Liquid inventory not initialized"
                )

            total_ml = (
                (liquid.get("red_ml") or 0)
                + (liquid.get("green_ml") or 0)
                + (liquid.get("blue_ml") or 0)
                + (liquid.get("dark_ml") or 0)
            )

            # Potions total
            potions_total = (
                connection.execute(
                    sqlalchemy.text("SELECT SUM(quantity) FROM potion_inventory")
                ).scalar()
                or 0
            )

            # Gold total
            gold = (
                connection.execute(
                    sqlalchemy.text("SELECT amount FROM gold_inventory LIMIT 1")
                ).scalar()
                or 0
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inventory query failed: {e}")

    return InventoryAudit(
        number_of_potions=potions_total,
        ml_in_barrels=total_ml,
        gold=gold,
    )


@router.post("/plan", response_model=CapacityPlan)
def get_capacity_plan():
    with db.engine.begin() as connection:
        gold = (
            connection.execute(
                sqlalchemy.text("SELECT amount FROM gold_inventory LIMIT 1")
            ).scalar()
            or 0
        )

    max_units = min(gold // 1000, 10)
    return CapacityPlan(
        potion_capacity=max_units // 2,
        ml_capacity=max_units - (max_units // 2),
    )


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def deliver_capacity_plan(capacity_purchase: CapacityPlan, order_id: str):
    cost = 1000 * (capacity_purchase.potion_capacity + capacity_purchase.ml_capacity)

    with db.engine.begin() as connection:
        # Idempotency check
        try:
            connection.execute(
                sqlalchemy.text("""
                    INSERT INTO processed_requests (order_id)
                    VALUES (:order_id)
                """),
                {"order_id": order_id},
            )
        except sqlalchemy.exc.IntegrityError:
            return  # already processed

        current_gold = connection.execute(
            sqlalchemy.text("SELECT amount FROM gold_inventory LIMIT 1")
        ).scalar()

        if current_gold is None or current_gold < cost:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough gold: required {cost}, available {current_gold}",
            )

        # Deduct gold
        connection.execute(
            sqlalchemy.text("""
                INSERT INTO ledger_entries (category, quantity, order_id, source)
                VALUES ('gold', :amount, :order_id, 'capacity-upgrade')
            """),
            {"amount": -cost, "order_id": order_id},
        )

        connection.execute(
            sqlalchemy.text("""
                UPDATE gold_inventory SET amount = amount - :amount
            """),
            {"amount": cost},
        )

        # Update capacity_inventory
        connection.execute(
            sqlalchemy.text("""
                INSERT INTO capacity_inventory (id, potion_capacity, ml_capacity)
                VALUES (1, :potion, :ml)
                ON CONFLICT (id)
                DO UPDATE SET
                    potion_capacity = capacity_inventory.potion_capacity + EXCLUDED.potion_capacity,
                    ml_capacity = capacity_inventory.ml_capacity + EXCLUDED.ml_capacity
            """),
            {
                "potion": capacity_purchase.potion_capacity,
                "ml": capacity_purchase.ml_capacity,
            },
        )
