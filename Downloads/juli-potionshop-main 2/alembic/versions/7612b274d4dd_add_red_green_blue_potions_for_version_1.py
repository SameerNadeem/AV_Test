"""Add red, green, blue potions for version 1

Revision ID: 7612b274d4dd
Revises: e91d0c24f7d0
Create Date: 2025-04-04 13:51:37.884952

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7612b274d4dd"
down_revision: Union[str, None] = "e91d0c24f7d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "global_inventory",
        sa.Column("red_ml", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "global_inventory",
        sa.Column("green_ml", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "global_inventory",
        sa.Column("blue_ml", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "global_inventory",
        sa.Column("red_potions", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "global_inventory",
        sa.Column("green_potions", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "global_inventory",
        sa.Column("blue_potions", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_check_constraint(
        "ck_red_ml_non_negative", "global_inventory", "red_ml >= 0"
    )
    op.create_check_constraint(
        "ck_green_ml_non_negative", "global_inventory", "green_ml >= 0"
    )
    op.create_check_constraint(
        "ck_blue_ml_non_negative", "global_inventory", "blue_ml >= 0"
    )
    op.create_check_constraint(
        "ck_red_potions_non_negative", "global_inventory", "red_potions >= 0"
    )
    op.create_check_constraint(
        "ck_green_potions_non_negative", "global_inventory", "green_potions >= 0"
    )
    op.create_check_constraint(
        "ck_blue_potions_non_negative", "global_inventory", "blue_potions >= 0"
    )


def downgrade():
    # Drop constraints if they exist
    op.execute(
        "ALTER TABLE IF EXISTS global_inventory DROP CONSTRAINT IF EXISTS ck_red_ml_non_negative"
    )
    op.execute(
        "ALTER TABLE IF EXISTS global_inventory DROP CONSTRAINT IF EXISTS ck_green_ml_non_negative"
    )
    op.execute(
        "ALTER TABLE IF EXISTS global_inventory DROP CONSTRAINT IF EXISTS ck_blue_ml_non_negative"
    )
    op.execute(
        "ALTER TABLE IF EXISTS global_inventory DROP CONSTRAINT IF EXISTS ck_red_potions_non_negative"
    )
    op.execute(
        "ALTER TABLE IF EXISTS global_inventory DROP CONSTRAINT IF EXISTS ck_green_potions_non_negative"
    )
    op.execute(
        "ALTER TABLE IF EXISTS global_inventory DROP CONSTRAINT IF EXISTS ck_blue_potions_non_negative"
    )

    # Drop columns if they exist (safe against missing table)
    for column in [
        "red_ml",
        "green_ml",
        "blue_ml",
        "red_potions",
        "green_potions",
        "blue_potions",
    ]:
        op.execute(
            f"ALTER TABLE IF EXISTS global_inventory DROP COLUMN IF EXISTS {column}"
        )
