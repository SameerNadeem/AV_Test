"""Re-add global_inventory

Revision ID: 519ff2ef7f06
Revises: 8f73a54373ba
Create Date: 2025-05-03 21:03:05.460666

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "519ff2ef7f06"
down_revision: Union[str, None] = "8f73a54373ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "global_inventory",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("gold", sa.Integer, nullable=False),
        sa.CheckConstraint("gold >= 0", name="check_gold_positive"),
    )
    op.execute(sa.text("INSERT INTO global_inventory (gold) VALUES (100)"))


def downgrade():
    op.drop_table("global_inventory")
