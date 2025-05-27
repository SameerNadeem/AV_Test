"""Recreate missing tables

Revision ID: d124929ba441
Revises: 6234a1a79eea
Create Date: 2025-05-03 23:17:23.292070

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d124929ba441"
down_revision: Union[str, None] = "6234a1a79eea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS carts (
            id SERIAL PRIMARY KEY,
            customer_name TEXT,
            checked_out BOOLEAN DEFAULT false
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            id SERIAL PRIMARY KEY,
            cart_id INTEGER NOT NULL,
            potion_sku TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            UNIQUE (cart_id, potion_sku)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS potions (
            sku TEXT PRIMARY KEY,
            price INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            active BOOLEAN DEFAULT true
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS potion_catalog (
            sku TEXT PRIMARY KEY,
            name TEXT,
            r INTEGER NOT NULL,
            g INTEGER NOT NULL,
            b INTEGER NOT NULL,
            d INTEGER NOT NULL,
            price INTEGER NOT NULL
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS ledger_entries (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL,
            sku TEXT,
            quantity INTEGER NOT NULL,
            order_id TEXT
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS global_inventory (
            id SERIAL PRIMARY KEY,
            gold INTEGER NOT NULL,
            red_ml INTEGER NOT NULL,
            green_ml INTEGER NOT NULL,
            blue_ml INTEGER NOT NULL,
            dark_ml INTEGER NOT NULL,
            red_potions INTEGER NOT NULL,
            green_potions INTEGER NOT NULL,
            blue_potions INTEGER NOT NULL
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS processed_requests (
            order_id TEXT PRIMARY KEY
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id SERIAL PRIMARY KEY,
            cart_id INTEGER NOT NULL,
            potion_sku TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT now()
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
