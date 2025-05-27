"""Add customer_name to carts

Revision ID: 563cfc239b56
Revises: 58239b781d35
Create Date: 2025-05-03 19:47:50.790833
"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "563cfc239b56"
down_revision: Union[str, None] = "58239b781d35"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = inspect(conn)

    for table in [
        "carts",
        "potions",
        "deliveries",
        "ledger_entries",
        "cart_items",
        "global_inventory",
        "audit_log",
    ]:
        if table in inspector.get_table_names():
            op.drop_table(table)


def downgrade() -> None:
    op.drop_column("carts", "customer_name")
