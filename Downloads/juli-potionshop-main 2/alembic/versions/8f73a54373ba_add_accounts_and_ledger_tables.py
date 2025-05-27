"""Add accounts and ledger tables

Revision ID: 8f73a54373ba
Revises: 563cfc239b56
Create Date: 2025-05-03 20:33:40.957454

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "8f73a54373ba"
down_revision: Union[str, None] = "563cfc239b56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    if "accounts" not in inspector.get_table_names():
        op.create_table(
            "accounts",
            sa.Column("id", sa.Integer, primary_key=True),
        )

    if "account_transactions" not in inspector.get_table_names():
        op.create_table(
            "account_transactions",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()")),
            sa.Column("description", sa.Text),
        )

    if "account_ledger_entries" not in inspector.get_table_names():
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


def downgrade():
    op.drop_table("account_ledger_entries", if_exists=True)
    op.drop_table("account_transactions", if_exists=True)
    op.drop_table("accounts", if_exists=True)
