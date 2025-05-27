"""Manually recreate missing tables

Revision ID: 6234a1a79eea
Revises: 519ff2ef7f06
Create Date: 2025-05-03 23:08:17.571261
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "6234a1a79eea"
down_revision: Union[str, None] = "519ff2ef7f06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()

    if "accounts" not in existing_tables:
        op.create_table(
            "accounts",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.String, nullable=True),
        )

    if "account_transactions" not in existing_tables:
        op.create_table(
            "account_transactions",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("created_at", sa.TIMESTAMP, server_default=sa.text("now()")),
            sa.Column("description", sa.Text),
        )

    if "account_ledger_entries" not in existing_tables:
        op.create_table(
            "account_ledger_entries",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("account_id", sa.Integer, sa.ForeignKey("accounts.id")),
            sa.Column(
                "account_transaction_id",
                sa.Integer,
                sa.ForeignKey("account_transactions.id"),
            ),
            sa.Column("change", sa.Integer),
        )

    if "global_inventory" not in existing_tables:
        op.create_table(
            "global_inventory",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("gold", sa.Integer, nullable=False),
            sa.Column("red_ml", sa.Integer, nullable=False, server_default="0"),
            sa.Column("green_ml", sa.Integer, nullable=False, server_default="0"),
            sa.Column("blue_ml", sa.Integer, nullable=False, server_default="0"),
            sa.Column("red_potions", sa.Integer, nullable=False, server_default="0"),
            sa.Column("green_potions", sa.Integer, nullable=False, server_default="0"),
            sa.Column("blue_potions", sa.Integer, nullable=False, server_default="0"),
            sa.CheckConstraint("gold >= 0"),
            sa.CheckConstraint("red_ml >= 0"),
            sa.CheckConstraint("green_ml >= 0"),
            sa.CheckConstraint("blue_ml >= 0"),
            sa.CheckConstraint("red_potions >= 0"),
            sa.CheckConstraint("green_potions >= 0"),
            sa.CheckConstraint("blue_potions >= 0"),
        )

    if "processed_requests" not in existing_tables:
        op.create_table(
            "processed_requests",
            sa.Column("order_id", sa.Text, primary_key=True),
            sa.Column("response", sa.JSON(), nullable=False),
        )


def downgrade() -> None:
    """Downgrade schema."""
    pass
