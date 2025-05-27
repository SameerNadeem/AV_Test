from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import sqlalchemy
from sqlalchemy import bindparam

from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class SearchSortOptions(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"


class SearchSortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class LineItem(BaseModel):
    line_item_id: int
    item_sku: str
    customer_name: str
    line_item_total: float


class SearchResponse(BaseModel):
    previous: Optional[str] = None
    next: Optional[str] = None
    results: List[LineItem]


@router.get("/search/", response_model=SearchResponse, tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: int = 0,
    sort_col: SearchSortOptions = SearchSortOptions.timestamp,
    sort_order: SearchSortOrder = SearchSortOrder.desc,
):
    limit = 50
    offset = search_page * limit

    query = f"""
        SELECT ci.id AS line_item_id, ci.potion_sku AS item_sku, c.customer_name, 
               ci.quantity * pc.price AS line_item_total
        FROM cart_items ci
        JOIN carts c ON ci.cart_id = c.id
        JOIN potion_catalog pc ON ci.potion_sku = pc.sku
        WHERE (:customer_name = '' OR c.customer_name ILIKE :customer_name_like)
          AND (:potion_sku = '' OR ci.potion_sku = :potion_sku)
        ORDER BY {sort_col.value} {sort_order.value}
        LIMIT :limit OFFSET :offset
    """

    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(query),
            {
                "customer_name": customer_name,
                "customer_name_like": f"%{customer_name}%",
                "potion_sku": potion_sku,
                "limit": limit,
                "offset": offset,
            },
        ).fetchall()

    return SearchResponse(
        previous=str(search_page - 1) if search_page > 0 else None,
        next=str(search_page + 1) if len(results) == limit else None,
        results=[LineItem(**row._mapping) for row in results],
    )


class Customer(BaseModel):
    customer_id: str
    customer_name: str
    character_class: str
    level: int = Field(ge=1, le=20)


@router.post("/visits/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_visits(visit_id: int, customers: List[Customer]):
    print(customers)
    pass


class CartCreateResponse(BaseModel):
    cart_id: int


@router.post("/", response_model=CartCreateResponse)
def create_cart(new_cart: Customer):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                INSERT INTO carts (customer_name)
                VALUES (:customer_name)
                RETURNING id
            """),
            {"customer_name": new_cart.customer_name},
        )
        return CartCreateResponse(cart_id=result.scalar_one())


class CartItem(BaseModel):
    quantity: int = Field(ge=1, description="Quantity must be at least 1")


@router.post("/{cart_id}/items/{item_sku}", status_code=status.HTTP_204_NO_CONTENT)
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""
                INSERT INTO cart_items (cart_id, potion_sku, quantity)
                VALUES (:cart_id, :item_sku, :quantity)
                ON CONFLICT (cart_id, potion_sku)
                DO UPDATE SET quantity = :quantity
            """),
            {"cart_id": cart_id, "item_sku": item_sku, "quantity": cart_item.quantity},
        )


class CheckoutResponse(BaseModel):
    total_potions_bought: int
    total_gold_paid: int


class CartCheckout(BaseModel):
    payment: str


@router.post("/{cart_id}/checkout", response_model=CheckoutResponse)
def checkout(cart_id: int, cart_checkout: CartCheckout):
    order_id = f"checkout-{cart_id}"

    with db.engine.begin() as connection:
        try:
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO processed_requests (order_id) VALUES (:order_id)"
                ),
                {"order_id": order_id},
            )
        except sqlalchemy.exc.IntegrityError:
            return CheckoutResponse(total_potions_bought=0, total_gold_paid=0)

        cart_items = connection.execute(
            sqlalchemy.text("""
                SELECT potion_sku, quantity FROM cart_items WHERE cart_id = :cart_id
            """),
            {"cart_id": cart_id},
        ).fetchall()

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        potion_prices = connection.execute(
            sqlalchemy.text("""
                SELECT sku, price FROM potion_catalog
                WHERE sku IN :sku_list
            """).bindparams(bindparam("sku_list", expanding=True)),
            {"sku_list": [item.potion_sku for item in cart_items]},
        ).fetchall()
        price_map = {row.sku: row.price for row in potion_prices}

        potion_inventory = connection.execute(
            sqlalchemy.text("SELECT sku, quantity FROM potion_inventory")
        ).fetchall()
        inventory_map = {row.sku: row.quantity for row in potion_inventory}

        total_gold_paid = 0
        total_potions_bought = 0

        for item in cart_items:
            sku = item.potion_sku
            qty = item.quantity

            if sku not in price_map:
                raise HTTPException(status_code=400, detail=f"Missing price for {sku}")

            if (inventory_map.get(sku) or 0) < qty:
                raise HTTPException(
                    status_code=400, detail=f"Not enough of {sku} in stock"
                )

            total_gold_paid += qty * price_map[sku]
            total_potions_bought += qty

        # subtract potion inventory and log potion ledger entries
        for item in cart_items:
            connection.execute(
                sqlalchemy.text("""
                    INSERT INTO ledger_entries (category, sub_type, quantity, order_id, source)
                    VALUES ('potion', :sku, :quantity, :order_id, 'checkout')
                """),
                {
                    "sku": item.potion_sku,
                    "quantity": -item.quantity,
                    "order_id": order_id,
                },
            )
            connection.execute(
                sqlalchemy.text("""
                    UPDATE potion_inventory
                    SET quantity = quantity - :qty
                    WHERE sku = :sku
                """),
                {"qty": item.quantity, "sku": item.potion_sku},
            )

        # add gold to shop and log to ledger
        connection.execute(
            sqlalchemy.text("""
                UPDATE gold_inventory
                SET amount = amount + :amount
            """),
            {"amount": total_gold_paid},
        )
        connection.execute(
            sqlalchemy.text("""
                INSERT INTO ledger_entries (category, quantity, order_id, source)
                VALUES ('gold', :amount, :order_id, 'checkout')
            """),
            {"amount": total_gold_paid, "order_id": order_id},
        )

        # mark cart as checked out
        connection.execute(
            sqlalchemy.text("UPDATE carts SET checked_out = TRUE WHERE id = :cart_id"),
            {"cart_id": cart_id},
        )

    return CheckoutResponse(
        total_potions_bought=total_potions_bought,
        total_gold_paid=total_gold_paid,
    )
