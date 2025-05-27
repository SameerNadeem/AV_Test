"""Add potions and cart tables for version 2

Revision ID: be75e857fcf7
Revises: 9174a835f253
Create Date: 2025-04-11 21:45:37.246706

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "be75e857fcf7"
down_revision: Union[str, None] = "9174a835f253"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "potions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku", sa.String(length=20), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("r", sa.Integer(), nullable=False),
        sa.Column("g", sa.Integer(), nullable=False),
        sa.Column("b", sa.Integer(), nullable=False),
        sa.Column("d", sa.Integer(), nullable=False),
        sa.CheckConstraint("r + g + b + d = 100", name="check_mix_sum"),
        sa.CheckConstraint("quantity >= 0", name="check_quantity_positive"),
    )

    op.create_table(
        "carts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cart_id", sa.Integer(), sa.ForeignKey("carts.id"), nullable=False),
        sa.Column(
            "potion_sku",
            sa.String(length=20),
            sa.ForeignKey("potions.sku"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.UniqueConstraint("cart_id", "potion_sku", name="uix_cart_potion"),
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS cart_items CASCADE")
    op.execute("DROP TABLE IF EXISTS carts CASCADE")
    op.execute("DROP TABLE IF EXISTS potions CASCADE")
