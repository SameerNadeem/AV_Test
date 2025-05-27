"""Merge order_id and processed_requests changes

Revision ID: 663fb6b0ac09
Revises: aa8e0698a303, 959e300864f0
Create Date: 2025-05-03 18:16:37.787046

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "663fb6b0ac09"
down_revision: Union[str, tuple[str, ...], None] = ("aa8e0698a303", "959e300864f0")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
