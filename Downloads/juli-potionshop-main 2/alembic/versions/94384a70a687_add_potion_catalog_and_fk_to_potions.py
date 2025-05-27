"""add potion_catalog and fk to potions

Revision ID: 94384a70a687
Revises: 89b00178c8c5
Create Date: 2025-04-16 10:00:10.704204

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "94384a70a687"
down_revision: Union[str, None] = "89b00178c8c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if "potion_catalog" not in inspector.get_table_names():
        op.create_table(
            "potion_catalog",
            sa.Column("sku", sa.String(), primary_key=True),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("price", sa.Integer(), nullable=False),
            sa.Column("r", sa.Integer(), nullable=False),
            sa.Column("g", sa.Integer(), nullable=False),
            sa.Column("b", sa.Integer(), nullable=False),
            sa.Column("d", sa.Integer(), nullable=False),
            sa.Column(
                "created_at",
                sa.TIMESTAMP(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.CheckConstraint("r BETWEEN 0 AND 100"),
            sa.CheckConstraint("g BETWEEN 0 AND 100"),
            sa.CheckConstraint("b BETWEEN 0 AND 100"),
            sa.CheckConstraint("d BETWEEN 0 AND 100"),
            sa.CheckConstraint("r + g + b + d = 100", name="valid_ratio"),
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS potions CASCADE")
    op.drop_table("potion_catalog")
