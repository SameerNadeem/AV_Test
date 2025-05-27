"""Add missing columns to ledger_entries

Revision ID: 4f49bbb06611
Revises: 9b4b3948fae3
Create Date: 2025-05-09 13:27:19.394168

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "4f49bbb06611"
down_revision: Union[str, None] = "9b4b3948fae3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # op.add_column("ledger_entries", sa.Column("category", sa.VARCHAR()))
    # op.add_column("ledger_entries", sa.Column("sub_type", sa.VARCHAR()))
    # op.add_column("ledger_entries", sa.Column("source", sa.VARCHAR()))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
