"""Initial clean state

Revision ID: c4b231cc3fd1
Revises: 663fb6b0ac09
Create Date: 2025-05-03 18:46:44.907733

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c4b231cc3fd1"
down_revision: Union[str, None] = "663fb6b0ac09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "processed_requests",
        sa.Column("order_id", sa.Text(), nullable=False),
        sa.Column("response", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("order_id"),
    )

    # Drop all existing tables that may have foreign key constraints
    op.execute("DROP TABLE IF EXISTS account_ledger_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS account_transactions CASCADE")
    op.execute("DROP TABLE IF EXISTS ledger_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS audit_log CASCADE")
    op.execute("DROP TABLE IF EXISTS potion_catalog CASCADE")
    op.execute("DROP TABLE IF EXISTS accounts CASCADE")

    # ### end Alembic commands ###


def downgrade():
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer, primary_key=True),
    )

    op.create_table(
        "account_transactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()")),
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
