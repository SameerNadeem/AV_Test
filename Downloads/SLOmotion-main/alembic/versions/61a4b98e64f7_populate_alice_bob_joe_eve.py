"""populate alice,bob,joe,eve

Revision ID: 61a4b98e64f7
Revises: 34a53ab6d376
Create Date: 2025-05-10 18:08:41.726936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from src import database as db
import sqlalchemy


# revision identifiers, used by Alembic.
revision: str = '61a4b98e64f7'
down_revision: Union[str, None] = '34a53ab6d376'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    connect = op.get_bind()
    mineMovie = connect.execute(sa.text("INSERT into movies (name,genre) VALUES ('A Minecraft Movie', 'Adventure') RETURNING id")).one().id
    barbieMovie = connect.execute(sa.text("INSERT into movies (name,genre) VALUES ('Barbie', 'Comedy') RETURNING id")).one().id

    aliceId = connect.execute(sa.text("INSERT into users (name) VALUES ('Alice') RETURNING id")).one().id
    aliceWId = connect.execute(sa.text("INSERT INTO watchlists (user_id, public) VALUES (:user_id, :public) RETURNING id"), [{"user_id": aliceId, "public": True}]).one().id
    bobId = connect.execute(sa.text("INSERT into users (name) VALUES ('Bob') RETURNING id")).one().id
    bobWId = connect.execute(sa.text("INSERT INTO watchlists (user_id, public) VALUES (:user_id, :public) RETURNING id"), [{"user_id": bobId, "public": True}]).one().id
    joeId = connect.execute(sa.text("INSERT into users (name) VALUES ('Joe') RETURNING id")).one().id
    joeWId = connect.execute(sa.text("INSERT INTO watchlists (user_id, public) VALUES (:user_id, :public) RETURNING id"), [{"user_id": joeId, "public": True}]).one().id
    eveId = connect.execute(sa.text("INSERT into users (name) VALUES ('Eve') RETURNING id")).one().id
    eveWId = connect.execute(sa.text("INSERT INTO watchlists (user_id, public) VALUES (:user_id, :public) RETURNING id"), [{"user_id": eveId, "public": True}]).one().id

    with db.engine.begin() as connection:
        gwhId = connection.execute(
            sa.text(
                """
                SELECT id 
                FROM movies
                WHERE name = 'Good Will Hunting'
                """
            )
        ).one().id

        gladiatorId = connection.execute(
            sa.text(
                """
                SELECT id 
                FROM movies
                WHERE name = 'Gladiator'
                """
            )
        ).one().id

        joeMineId = connect.execute(sa.text("INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, '', :rating, 'want to watch') RETURNING id"), [{"movie_id": mineMovie, "user_id": joeId, "rating": None}]).one().id
        joeGwhId = connect.execute(sa.text("INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'amazing cinematography', 5, 'watched') RETURNING id"), [{"movie_id": gwhId, "user_id": joeId}]).one().id
        connect.execute(sa.text("INSERT into watchlist_movie (watchlist_id, movie_rating_id) VALUES (:watchlist_id, :movie_rating_id)"), [{"watchlist_id": joeWId, "movie_rating_id": joeMineId}])
        connect.execute(sa.text("INSERT into watchlist_movie (watchlist_id, movie_rating_id) VALUES (:watchlist_id, :movie_rating_id)"), [{"watchlist_id": joeWId, "movie_rating_id": joeGwhId}])
        
        bobGladId = connect.execute(sa.text("INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'nice', 6, 'watched') RETURNING id"), [{"movie_id": gladiatorId, "user_id": bobId}]).one().id
        bobGwhId = connect.execute(sa.text("INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'really good', 7, 'watched') RETURNING id"), [{"movie_id": gwhId, "user_id": bobId}]).one().id
        connect.execute(sa.text("INSERT into watchlist_movie (watchlist_id, movie_rating_id) VALUES (:watchlist_id, :movie_rating_id)"), [{"watchlist_id": bobWId, "movie_rating_id": bobGladId}])
        connect.execute(sa.text("INSERT into watchlist_movie (watchlist_id, movie_rating_id) VALUES (:watchlist_id, :movie_rating_id)"), [{"watchlist_id": bobWId, "movie_rating_id": bobGwhId}])
    
        aliceBarbieId = connect.execute(sa.text("INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, '', :rating, 'want to watch') RETURNING id"), [{"movie_id": barbieMovie, "user_id": aliceId, "rating": None}]).one().id
        connect.execute(sa.text("INSERT into watchlist_movie (watchlist_id, movie_rating_id) VALUES (:watchlist_id, :movie_rating_id)"), [{"watchlist_id": aliceWId, "movie_rating_id": aliceBarbieId}])

        eveGladId = connect.execute(sa.text("INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'nice', 6, 'watched') RETURNING id"), [{"movie_id": gladiatorId, "user_id": eveId}]).one().id
        eveGwhId = connect.execute(sa.text("INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'enjoyed', 7, 'watched') RETURNING id"), [{"movie_id": gwhId, "user_id": eveId}]).one().id
        connect.execute(sa.text("INSERT into watchlist_movie (watchlist_id, movie_rating_id) VALUES (:watchlist_id, :movie_rating_id)"), [{"watchlist_id": eveWId, "movie_rating_id": eveGladId}])
        connect.execute(sa.text("INSERT into watchlist_movie (watchlist_id, movie_rating_id) VALUES (:watchlist_id, :movie_rating_id)"), [{"watchlist_id": eveWId, "movie_rating_id": eveGwhId}])
        eveBarbieId = connect.execute(sa.text("INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'inspiring', 7, 'watched') RETURNING id"), [{"movie_id": barbieMovie, "user_id": eveId}]).one().id
        connect.execute(sa.text("INSERT into watchlist_movie (watchlist_id, movie_rating_id) VALUES (:watchlist_id, :movie_rating_id)"), [{"watchlist_id": eveWId, "movie_rating_id": eveBarbieId}])


def downgrade() -> None:
    """Downgrade schema."""
    pass
