from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    dependencies=[Depends(auth.get_api_key)],
)


class Rating(BaseModel):
    user_id: int
    rating: int | None

@router.get("/{movie_name}", response_model=int)
def get_movie_id(movie_name: str) -> int:
    with db.engine.connect() as connection:
        id = connection.execute(
            sqlalchemy.text
            (
                """
                SELECT id
                FROM movies
                WHERE name = :movie_name
                """
            ), {"movie_name": movie_name}
        ).one_or_none()

        if id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie name not formatted correctly or not in IMDb top 250 list",
            )

        return id.id
    

@router.get("/ratings/{movie_id}", response_model=List[Rating])
def get_movie_ratings(movie_id: int) -> List[Rating]:
    with db.engine.connect() as conn:
        results = conn.execute(sqlalchemy.text(
            """
            SELECT user_id, rating
            FROM movie_ratings
            WHERE movie_id = :movie_id
            """
        ), {"movie_id": movie_id}).mappings().all()

        ratings = []
        for row in results:
            ratings.append(Rating(
                user_id = row.user_id,
                rating = row.rating
            ))

        return ratings