from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


# --- Users ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    ratings = relationship("MovieRating", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    watchlists = relationship("Watchlist", back_populates="user")


# --- Movies ---
class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    genre = Column(String, nullable=False)

    ratings = relationship("MovieRating", back_populates="movie")
    comments = relationship("Comment", back_populates="movie")


# --- Movie Ratings ---
class MovieRating(Base):
    __tablename__ = "movie_ratings"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(String)
    rating = Column(Integer)
    status = Column(String)

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")
    watchlist_movies = relationship("WatchlistMovie", back_populates="movie_rating")


# --- Comments ---
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    commenter_user_id = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    comment_text = Column(String)

    user = relationship("User", back_populates="comments")
    movie = relationship("Movie", back_populates="comments")


# --- Watchlist ---
class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    public = Column(Boolean, default=False)

    user = relationship("User", back_populates="watchlists")
    movies = relationship("WatchlistMovie", back_populates="watchlist")


# --- Join Table: Watchlist <-> MovieRating ---
class WatchlistMovie(Base):
    __tablename__ = "watchlist_movie"

    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), primary_key=True)
    movie_rating_id = Column(Integer, ForeignKey("movie_ratings.id"), primary_key=True)

    watchlist = relationship("Watchlist", back_populates="movies")
    movie_rating = relationship("MovieRating", back_populates="watchlist_movies")
