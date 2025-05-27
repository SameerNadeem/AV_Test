"""Add audit_log table

Revision ID: 89b00178c8c5
Revises: be75e857fcf7
Create Date: 2025-04-12 16:32:36.652253

"""

from alembic import op
import sqlalchemy as sa
from typing import Union, Sequence

revision: str = "89b00178c8c5"
down_revision: Union[str, None] = "be75e857fcf7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cart_id", sa.Integer(), nullable=False),
        sa.Column("potion_sku", sa.String(length=20), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS audit_log CASCADE")
