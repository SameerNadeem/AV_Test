"""create tables

Revision ID: 9b4b3948fae3
Revises: e52d702341b6
Create Date: 2025-05-05 16:04:12.746123

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9b4b3948fae3"
down_revision: Union[str, None] = "e52d702341b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — create all necessary tables."""

    op.create_table(
        "potions",
        sa.Column("sku", sa.VARCHAR(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("price", sa.INTEGER(), nullable=False),
        sa.Column("quantity", sa.INTEGER(), nullable=False),
        sa.Column("active", sa.BOOLEAN(), server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("sku"),
    )

    op.create_table(
        "potion_inventory",
        sa.Column("sku", sa.TEXT(), nullable=False),
        sa.Column(
            "quantity", sa.INTEGER(), server_default=sa.text("0"), nullable=False
        ),
        sa.PrimaryKeyConstraint("sku"),
    )

    op.create_table(
        "liquid_inventory",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column("red_ml", sa.INTEGER(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "green_ml", sa.INTEGER(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column("blue_ml", sa.INTEGER(), server_default=sa.text("0"), nullable=False),
        sa.Column("dark_ml", sa.INTEGER(), server_default=sa.text("0"), nullable=False),
    )

    op.create_table(
        "capacity_inventory",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column(
            "ml_capacity", sa.INTEGER(), server_default=sa.text("1"), nullable=False
        ),
        sa.Column(
            "potion_capacity", sa.INTEGER(), server_default=sa.text("1"), nullable=False
        ),
    )

    op.create_table(
        "cart_items",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column("cart_id", sa.INTEGER(), nullable=False),
        sa.Column("potion_sku", sa.TEXT(), nullable=False),
        sa.Column("quantity", sa.INTEGER(), nullable=False),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()")
        ),
        sa.UniqueConstraint(
            "cart_id", "potion_sku", name="cart_items_cartid_sku_unique"
        ),
    )

    op.create_table(
        "potion_catalog",
        sa.Column("sku", sa.VARCHAR(), nullable=False),
        sa.Column("name", sa.VARCHAR()),
        sa.Column("r", sa.INTEGER()),
        sa.Column("g", sa.INTEGER()),
        sa.Column("b", sa.INTEGER()),
        sa.Column("d", sa.INTEGER()),
        sa.Column("price", sa.INTEGER()),
        sa.Column("active", sa.BOOLEAN()),
        sa.PrimaryKeyConstraint("sku"),
    )

    op.create_table(
        "global_inventory",
        sa.Column("id", sa.INTEGER(), primary_key=True),
        sa.Column("gold", sa.INTEGER()),
        sa.Column("red_ml", sa.INTEGER(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "green_ml", sa.INTEGER(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column("blue_ml", sa.INTEGER(), server_default=sa.text("0"), nullable=False),
        sa.Column("dark_ml", sa.INTEGER(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "red_potions", sa.INTEGER(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "green_potions", sa.INTEGER(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "blue_potions", sa.INTEGER(), server_default=sa.text("0"), nullable=False
        ),
    )

    op.create_table(
        "carts",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column("customer_name", sa.TEXT()),
        sa.Column("checked_out", sa.BOOLEAN(), server_default=sa.text("false")),
        sa.Column("timestamp", postgresql.TIMESTAMP(), server_default=sa.text("now()")),
    )

    op.create_table(
        "processed_requests",
        sa.Column("order_id", sa.TEXT(), primary_key=True),
    )

    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column("type", sa.VARCHAR(), nullable=False),
        sa.Column("sku", sa.VARCHAR()),
        sa.Column("quantity", sa.INTEGER()),
        sa.Column("order_id", sa.TEXT()),
        sa.Column("source", sa.VARCHAR()),
        sa.Column("category", sa.VARCHAR()),
        sa.Column("sub_type", sa.VARCHAR()),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()")
        ),
        sa.Column(
            "timestamp",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("amount", sa.INTEGER()),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column("cart_id", sa.INTEGER()),
        sa.Column("potion_sku", sa.TEXT()),
        sa.Column("quantity", sa.INTEGER()),
        sa.Column("timestamp", postgresql.TIMESTAMP()),
        sa.Column("alembic_version", sa.VARCHAR()),
        sa.ForeignKeyConstraint(["cart_id"], ["carts.id"], name="fk_audit_log_cart"),
        sa.ForeignKeyConstraint(
            ["potion_sku"], ["potions.sku"], name="fk_audit_log_potion"
        ),
    )

    op.create_table(
        "gold_inventory",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column("amount", sa.INTEGER(), server_default=sa.text("0"), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema — drop all created tables."""

    op.drop_table("gold_inventory")
    op.drop_table("audit_log")
    op.drop_table("ledger_entries")
    op.drop_table("processed_requests")
    op.drop_table("carts")
    op.drop_table("global_inventory")
    op.drop_table("potion_catalog")
    op.drop_table("cart_items")
    op.drop_table("capacity_inventory")
    op.drop_table("liquid_inventory")
    op.drop_table("potion_inventory")
    op.drop_table("potions")
