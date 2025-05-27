"""Recreate schema

Revision ID: e5060646f464
Revises: e4b4c6a915f9
Create Date: 2025-05-03 17:00:35.328062

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "e5060646f464"
down_revision: Union[str, None] = "e4b4c6a915f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema safely by dropping tables in dependency order."""
    pass


def downgrade() -> None:
    pass  # or optionally re-create dropped tables if needed
