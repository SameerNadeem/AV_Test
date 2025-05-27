from fastapi import APIRouter, Depends, status
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset():
    """
    Reset the game state:
    - Gold set to 100
    - All potion ml types reset to 0
    - All potion inventory cleared
    - Capacity reset to 1 for potions and liquid
    - Ledger and processed requests cleared
    """
    with db.engine.begin() as connection:
        # clear state tables
        connection.execute(sqlalchemy.text("DELETE FROM ledger_entries"))
        connection.execute(sqlalchemy.text("DELETE FROM processed_requests"))
        connection.execute(sqlalchemy.text("DELETE FROM potion_inventory"))
        connection.execute(sqlalchemy.text("DELETE FROM capacity_inventory"))

        # insert starting gold into ledger
        connection.execute(
            sqlalchemy.text("""
            INSERT INTO ledger_entries (category, sub_type, quantity, order_id, source)
            VALUES ('gold', 'initial', 100, 'reset', 'admin')
        """)
        )

        # initialize capacity
        connection.execute(
            sqlalchemy.text("""
            INSERT INTO capacity_inventory (ml_capacity, potion_capacity)
            VALUES (1, 1)
        """)
        )
