"""
Movie Service
Handles movie metadata lookup, search, pagination, and user interaction augmentation.
"""

import sqlite3
from typing import Optional, List, Dict
from fastapi import HTTPException, status

from backend.app.recommender.engine import RecommenderEngine
from backend.app.schemas.schemas import MovieDetailOut, MovieBase, MovieListResponse, UserOut

def get_movie_details(
    movie_id: int,
    db: sqlite3.Connection,
    current_user: Optional[UserOut] = None
) -> MovieDetailOut:
    """Fetch movie details augmented with current user rating/favorite state."""
    engine = RecommenderEngine.get_instance()
    movie = engine.get_movie(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found."
        )

    user_rating = None
    is_favorite = False
    in_history = False

    if current_user:
        cursor = db.cursor()
        
        # Check rating
        cursor.execute("SELECT rating FROM user_ratings WHERE user_id = ? AND movie_id = ?", (current_user.id, movie_id))
        r_row = cursor.fetchone()
        if r_row:
            user_rating = float(r_row['rating'])

        # Check favorite
        cursor.execute("SELECT id FROM user_favorites WHERE user_id = ? AND movie_id = ?", (current_user.id, movie_id))
        if cursor.fetchone():
            is_favorite = True

        # Check history
        cursor.execute("SELECT id FROM user_history WHERE user_id = ? AND movie_id = ?", (current_user.id, movie_id))
        if cursor.fetchone():
            in_history = True

    similar = engine.get_similar_movies(movie_id, top_n=8)
    similar_movies = [MovieBase(**s) for s in similar]

    return MovieDetailOut(
        **movie,
        user_rating=user_rating,
        is_favorite=is_favorite,
        in_history=in_history,
        similar_movies=similar_movies
    )

def list_popular_movies(
    genre: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> MovieListResponse:
    """List popular movies with pagination and optional genre filter."""
    engine = RecommenderEngine.get_instance()
    movies_data, total = engine.get_popular(genre=genre, page=page, limit=limit)
    has_next = (page * limit) < total
    return MovieListResponse(
        movies=[MovieBase(**m) for m in movies_data],
        total=total,
        page=page,
        limit=limit,
        has_next=has_next
    )

def search_movies(
    query: str = "",
    genre: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> MovieListResponse:
    """Search movies with pagination."""
    engine = RecommenderEngine.get_instance()
    movies_data, total = engine.search_movies(query=query, genre=genre, page=page, limit=limit)
    has_next = (page * limit) < total
    return MovieListResponse(
        movies=[MovieBase(**m) for m in movies_data],
        total=total,
        page=page,
        limit=limit,
        has_next=has_next
    )
