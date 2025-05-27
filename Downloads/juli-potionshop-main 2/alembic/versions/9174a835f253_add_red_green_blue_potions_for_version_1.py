"""Add red, green, blue potions for version 1

Revision ID: 9174a835f253
Revises: 7612b274d4dd
Create Date: 2025-04-04 21:16:28.714432

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "9174a835f253"
down_revision: Union[str, None] = "7612b274d4dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
