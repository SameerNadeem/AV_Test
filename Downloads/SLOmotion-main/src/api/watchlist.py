from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import List, Literal
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/watchlist",
    tags=["watchlist"],
    dependencies=[Depends(auth.get_api_key)],
)


class WatchlistMovie(BaseModel):
    watchlist_id: int
    movie_id: int
    name: str
    status: str


class MovieRating(BaseModel):
    movie_id: int
    user_id: int
    notes: str
    rating: int | None = None
    status: Literal["watched", "want to watch", "watching"]

class WatchedMovie(BaseModel):
    movie_id: int
    title: str
    status: str
    rating: int
    genre: str

class AddToWatchlist(BaseModel):
    rating: int | None = None
    notes: str | None = None
    status: Literal["watched", "want to watch", "watching"]



@router.get("/{user_id}/watched", response_model=List[WatchedMovie])
def get_watched(user_id: int) -> List[WatchedMovie]:
    print(user_id)
    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """ 
                    SELECT id, public
                    FROM watchlists
                    WHERE user_id = :user_id
                """
            ),
            [{"user_id": user_id}],
        ).one_or_none()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't exist",
            )
        watchlist_id = row.id
        print(row)
        # Then from that get all the movie_rating ids associated with watchlist id
        print(watchlist_id)
        result = connection.execute(
            sqlalchemy.text(
                """
                    SELECT watchlist_id, movies.id as movie_id, movies.name as name, movie_ratings.status as status, movie_ratings.rating as rating, movies.genre as genre
                    FROM watchlist_movie
                    JOIN movie_ratings on watchlist_movie.movie_rating_id = movie_ratings.id
                    JOIN movies on movie_ratings.movie_id = movies.id
                    WHERE watchlist_id = :watchlist_id and status = 'watched'
                """
            ),
            [{"watchlist_id": watchlist_id}],
        ).tuples()
        #for all movie rating ids return the movie_rating, movie_ids, and their names
        watched_movies = []
        for movie in result:
            print(movie)
            watched_movies.append(
                WatchedMovie(
                    movie_id=movie.movie_id,
                    title = movie.name,
                    status = movie.status,
                    rating = movie.rating,
                    genre = movie.genre
                )
            )
        return watched_movies

@router.get("/{user_id}", response_model=List[WatchlistMovie])
def get_watchlist_movies(
    user_id: int,
) -> List[WatchlistMovie]:  # return list of movies on user's watchlist
    # get their watchlist id from watchlists?
    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """ 
                    SELECT id, public
                    FROM watchlists
                    WHERE user_id = :user_id
                """
            ),
            [{"user_id": user_id}],
        ).one_or_none()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't exist",
            )
        watchlist_id = row.id
        # Then from that get all the movie_rating ids associated with watchlist id
        result = connection.execute(
            sqlalchemy.text(
                """
                    SELECT watchlist_id, movies.id as movie_id, movies.name as name, status
                    FROM watchlist_movie
                    JOIN movie_ratings on watchlist_movie.movie_rating_id = movie_ratings.id
                    JOIN movies on movie_ratings.movie_id = movies.id
                    WHERE watchlist_id = :watchlist_id
                """
            ),
            [{"watchlist_id": watchlist_id}],
        ).tuples()
        # for all movie rating ids return the movie_rating, movie_ids, and their names
        watchlist_movies = []
        for movie in result:
            watchlist_movies.append(
                WatchlistMovie(
                    watchlist_id=movie.watchlist_id,
                    movie_id=movie.movie_id,
                    name=movie.name,
                    status = movie.status
                )
            )
        return watchlist_movies


@router.get("/{user_id}/{movie_id}", response_model=MovieRating)
def get_movie_rating(
    user_id: int, movie_id: int
) -> MovieRating:  # return a movie rating
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT movie_id, user_id, notes, rating, status
                FROM movie_ratings
                WHERE user_id = :user_id AND movie_id = :movie_id
                """
            ),
            {"user_id": user_id, "movie_id": movie_id},
        ).one_or_none()
        # if no result was found, raise a 404 HTTPException
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie rating not found for this user.",
            )
        # if result is found, return it as a MovieRating response model
        return MovieRating(
            movie_id=result.movie_id,
            user_id=result.user_id,
            notes=result.notes,
            rating=result.rating,
            status=result.status
        )

class CommentInput(BaseModel):
    comment_text: str

@router.post("/{user_id}/{movie_id}/{user2_id}/comment",status_code=status.HTTP_204_NO_CONTENT)
def post_comment_on_movie_rating(user_id: int, movie_id: int, user2_id: int, comment: CommentInput):
    with db.engine.begin() as connection:
        rating = connection.execute(sqlalchemy.text(
            """
            SELECT 1
            FROM movie_ratings
            WHERE user_id = :user_id AND movie_id = :movie_id
            """
        ), {"user_id": user_id, "movie_id": movie_id}).one_or_none()

        if rating is None:
            raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail="Movie or user does not exist.",)

        # insert comment
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO comments (commenter_user_id, user_id, movie_id, comment_text)
            VALUES (:commenter_user_id, :user_id, :movie_id, :comment_text)
            """
        ), {"commenter_user_id": user2_id, "user_id": user_id, "movie_id": movie_id, "comment_text": comment.comment_text})

    return {"message": "Comment added."}


@router.patch("/{user_id}/{movie_id}",status_code=status.HTTP_200_OK)
def update_watchlist_movie_entry(user_id: int, movie_id: int, update: MovieRating):
    # Updates a user's description/rating for a movie in their watchlist

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                UPDATE movie_ratings
                SET notes = :notes, rating = :rating, status = :status
                WHERE user_id = :user_id AND movie_id = :movie_id"""
            ),
            {"user_id": user_id, "movie_id": movie_id, "notes": update.notes, "rating": update.rating, "status": update.status},
        )

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie rating not found for this user.")
        
    return {"message" : "Successfully updated!"}


@router.post("/{user_id}/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_movie_onto_watchlist(user_id:int, movie_id:int, movie: AddToWatchlist):
    # posts in watchlist movie and movie ratings but in movie ratings it won't have rating or notes?

    # check if movie already exists in watchlist
    with db.engine.begin() as connection:
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT id 
                FROM movie_ratings
                WHERE user_id = :user_id AND movie_id = :movie_id
                """
            ),
            {"user_id": user_id, "movie_id": movie_id}
        ).one_or_none()

        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Movie already exists in watchlist.")
        
        # if it doesn't exist, insert into movie ratings table
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO movie_ratings (user_id, movie_id, notes, rating, status)
                VALUES (:user_id, :movie_id, :notes, :rating, :status)
                RETURNING id
                """
            ),
            {"user_id": user_id, "movie_id": movie_id, "notes": movie.notes or "N/A", "rating": movie.rating if movie.rating is not None else None, "status": movie.status}
        )

        movie_rating_id = result.scalar()

        # get the watchlist id for the user
        watchlist = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM watchlists
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id}
        ).one()

        # insert into watchlist_movie table
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO watchlist_movie (watchlist_id, movie_rating_id)
                VALUES (:watchlist_id, :movie_rating_id)
                """
            ),
            {"watchlist_id": watchlist.id, "movie_rating_id": movie_rating_id}
        )
    
    return {"message": "Successfully added movie to watchlist."}

@router.delete("/{user_id}/{movie_id}", status_code=status.HTTP_200_OK)
def delete_users_movie_entry(user_id: int, movie_id: int):
    # delete from movie ratings, watchlist movies, and any comments on it
    
    # gets movie rating id from movie ratings table
    with db.engine.begin() as connection:
        rating = connection.execute(
            sqlalchemy.text(
                """
                SELECT id 
                FROM movie_ratings
                WHERE user_id = :user_id AND movie_id = :movie_id
                """
            ),
            {"user_id": user_id, "movie_id": movie_id}
        ).one_or_none()

        if rating is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie rating not found for this user and movie.")
        
        movie_rating_id = rating.id

        # delete comments linked to the movie rating
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM comments
                WHERE user_id = :user_id AND movie_id = :movie_id
                """
            ),
            {"user_id": user_id, "movie_id": movie_id}
        )

        # delete from watchlist_movie table
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM watchlist_movie
                WHERE movie_rating_id = :movie_rating_id
                """
            ),
            {"movie_rating_id": movie_rating_id}
        )

        # delete from movie ratings table
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM movie_ratings
                WHERE id = :movie_rating_id
                """
            ),
            {"movie_rating_id": movie_rating_id}
        )

    return {"message": "Successfully removed movie."}