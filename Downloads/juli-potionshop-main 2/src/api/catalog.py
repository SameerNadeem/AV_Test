from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Annotated
from src import database as db
import sqlalchemy

router = APIRouter()


class CatalogItem(BaseModel):
    sku: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_]{1,20}$")]
    name: str
    quantity: Annotated[int, Field(ge=1, le=10000)]
    price: Annotated[int, Field(ge=1, le=500)]
    potion_type: List[int] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d]",
    )


@router.get("/catalog/", tags=["catalog"], response_model=List[CatalogItem])
def get_catalog() -> List[CatalogItem]:
    """
    Retrieves the catalog of items from the potions and potion_catalog tables.
    Only potions marked as active and with quantity > 0 will be shown.
    Limit of 6 potion SKUs at a time.
    """
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                SELECT 
                    pc.sku, pc.name, pc.price, pc.r, pc.g, pc.b, pc.d,
                    pi.quantity
                FROM potion_catalog pc
                JOIN potion_inventory pi ON pc.sku = pi.sku
                JOIN potions p ON pc.sku = p.sku
                WHERE p.active IS TRUE AND pi.quantity > 0
                LIMIT 6;
            """)
        ).fetchall()

    catalog = [
        CatalogItem(
            sku=row.sku,
            name=row.name,
            price=row.price,
            quantity=row.quantity,
            potion_type=[row.r, row.g, row.b, row.d],
        )
        for row in result
    ]

    return catalog
