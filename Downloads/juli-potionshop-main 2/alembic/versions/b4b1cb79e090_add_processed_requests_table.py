"""Add processed_requests table

Revision ID: b4b1cb79e090
Revises: 94384a70a687
Create Date: 2025-04-27 21:30:45.847633

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b4b1cb79e090"
down_revision: Union[str, None] = "94384a70a687"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("sku", sa.String, nullable=True),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("order_id", sa.UUID, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer, primary_key=True),
        # add other user metadata fields as needed
    )
    op.create_table(
        "account_transactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.text("now()")),
        sa.Column("description", sa.Text),
    )
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
    pass
