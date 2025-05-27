"""Add new features

Revision ID: 58239b781d35
Revises: c4b231cc3fd1
Create Date: 2025-05-03 19:16:01.373269
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "58239b781d35"
down_revision: Union[str, None] = "c4b231cc3fd1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop tables if they already exist
    op.execute("DROP TABLE IF EXISTS audit_log CASCADE")
    op.execute("DROP TABLE IF EXISTS cart_items CASCADE")
    op.execute("DROP TABLE IF EXISTS carts CASCADE")
    op.execute("DROP TABLE IF EXISTS deliveries CASCADE")
    op.execute("DROP TABLE IF EXISTS potions CASCADE")
    op.execute("DROP TABLE IF EXISTS ledger_entries CASCADE")

    # Recreate all tables
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cart_id", sa.Integer, nullable=False),
        sa.Column("potion_sku", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("timestamp", sa.TIMESTAMP(), nullable=False),
    )

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cart_id", sa.Integer, nullable=False),
        sa.Column("potion_sku", sa.String, nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
    )

    op.create_table(
        "carts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()")),
    )

    op.create_table(
        "deliveries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cart_id", sa.Integer, nullable=False),
        sa.Column("order_id", sa.Text, nullable=True),
        sa.Column("delivered_at", sa.TIMESTAMP(), nullable=True),
    )

    op.create_table(
        "potions",
        sa.Column("sku", sa.String, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("price", sa.Integer, nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("active", sa.Boolean, server_default=sa.text("true")),
    )

    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("sku", sa.String, nullable=True),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("order_id", sa.UUID, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS potions CASCADE")
    op.execute("DROP TABLE IF EXISTS deliveries CASCADE")
    op.execute("DROP TABLE IF EXISTS carts CASCADE")
    op.execute("DROP TABLE IF EXISTS cart_items CASCADE")
    op.execute("DROP TABLE IF EXISTS audit_log CASCADE")
    op.execute("DROP TABLE IF EXISTS ledger_entries CASCADE")
