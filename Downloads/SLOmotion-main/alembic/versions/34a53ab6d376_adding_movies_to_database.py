"""adding movies to database

Revision ID: 34a53ab6d376
Revises: 7c3197e783d3
Create Date: 2025-05-09 13:50:30.259914

"""
from typing import Sequence, Union
from sqlalchemy import table, column, String, Integer

from alembic import op
import sqlalchemy as sa
import csv
import os


# revision identifiers, used by Alembic.
revision: str = '34a53ab6d376'
down_revision: Union[str, None] = '7c3197e783d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    movies_table = table(
        'movies',
        column('name', String),
        column('genre', String),
    )
    base_dir = os.path.dirname('imdbmovies.csv')
    csv_path = os.path.join(base_dir, 'imdbmovies.csv')
    with open(csv_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        rows = []
        for row in reader:
            rows.append({'name': row['name'], 'genre': row['genre']})
    op.bulk_insert(movies_table, rows)
        

def downgrade() -> None:
    """Downgrade schema."""
    pass
