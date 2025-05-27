"""Changed order_id column to TEXT

Revision ID: aa8e0698a303
Revises: b4b1cb79e090
Create Date: 2025-05-03 00:30:22.449465
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "aa8e0698a303"
down_revision: Union[str, None] = "b4b1cb79e090"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    if "deliveries" in inspector.get_table_names():
        op.alter_column(
            "deliveries",
            "order_id",
            existing_type=sa.Integer(),
            type_=sa.Text(),
            existing_nullable=False,
        )
    else:
        print("Skipping: 'deliveries' table does not exist.")


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    if "deliveries" in inspector.get_table_names():
        op.alter_column(
            "deliveries",
            "order_id",
            existing_type=sa.Text(),
            type_=sa.Integer(),
            existing_nullable=False,
        )
    else:
        print("Skipping: 'deliveries' table does not exist.")
