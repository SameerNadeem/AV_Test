from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/recommended_movies",
    tags=["recommended"],
    dependencies=[Depends(auth.get_api_key)],
)

class Movie(BaseModel):
    movie_id: int
    name: str
    genre: str

@router.get("/{user_id}", response_model=List[Movie])
def get_recommended_movies(user_id: int) -> List[Movie]:
    with db.engine.connect() as conn:
        # Check if user exists
        result = conn.execute(sqlalchemy.text(
            "SELECT id FROM users WHERE id = :user_id"
        ), {"user_id": user_id}).fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Get genres of movies in user's watchlist
        watchlist = conn.execute(sqlalchemy.text(
            """
            SELECT m.genre
            FROM watchlists w
            JOIN watchlist_movie wm ON w.id = wm.watchlist_id
            JOIN movie_ratings mr ON wm.movie_rating_id = mr.id
            JOIN movies m ON mr.movie_id = m.id
            WHERE w.user_id = :user_id
            """
        ), {"user_id": user_id}).fetchall()

        if not watchlist:
            # No watchlist: return first 5 movies
            movies = conn.execute(sqlalchemy.text(
                "SELECT id AS movie_id, name, genre FROM movies LIMIT 5"
            )).mappings().all()
        else:
            # Get most common genre
            genre_counts = {}
            for row in watchlist:
                genre_counts[row.genre] = genre_counts.get(row.genre, 0) + 1
            top_genre = max(genre_counts, key=genre_counts.get)

            # Return 5 movies from top genre
            movies = conn.execute(sqlalchemy.text(
                """
                SELECT id AS movie_id, name, genre
                FROM movies
                WHERE genre = :genre
                LIMIT 5
                """
            ), {"genre": top_genre}).mappings().all()

        return [Movie(**row) for row in movies]
