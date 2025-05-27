"""Initial migration

Revision ID: e4b4c6a915f9
Revises: None
Create Date: 2025-05-03 16:57:38.527739

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "e4b4c6a915f9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if "deliveries" in inspector.get_table_names():
        op.alter_column("deliveries", "order_id", type_=sa.Text())
    else:
        print("Skipping: 'deliveries' table does not exist.")


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if "deliveries" in inspector.get_table_names():
        op.alter_column("deliveries", "order_id", type_=sa.Integer())
    else:
        print("Skipping: 'deliveries' table does not exist.")
