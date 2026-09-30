"""
Interaction Service
Handles business logic for ratings, likes/favorites, and watch history.
Decoupled from FastAPI HTTP layer.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

from backend.app.database import crud
from backend.app.schemas.schemas import (
    RatingOut, FavoriteOut, HistoryOut, InteractionSummary,
    LikeResponse, WatchResponse
)
from backend.app.recommender.popularity import get_recommender_instance
from backend.app.utils.helpers import get_poster_url


def _get_movie_info(movie_id: int) -> Optional[dict]:
    pop = get_recommender_instance()
    return pop.get_movie_metadata(movie_id)


def submit_rating(db: sqlite3.Connection, user_id: int, movie_id: int, rating: float) -> RatingOut:
    """Validate and record user rating for a movie."""
    movie = _get_movie_info(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {movie_id} does not exist in catalog."
        )

    crud.save_rating(db, user_id, movie_id, rating)

    return RatingOut(
        movie_id=movie_id,
        user_id=user_id,
        rating=rating,
        title=movie.get('title'),
        year=movie.get('year'),
        poster_url=movie.get('poster_url') or get_poster_url(movie_id, movie.get('tmdb_id_int')),
        genres_list=movie.get('genres_list', []),
        created_at="Just now"
    )


def delete_user_rating(db: sqlite3.Connection, user_id: int, movie_id: int) -> dict:
    """Remove a user's rating."""
    deleted = crud.delete_rating(db, user_id, movie_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rating for movie ID {movie_id} was not found."
        )
    return {"message": "Rating removed successfully.", "movie_id": movie_id}


def get_user_ratings_list(db: sqlite3.Connection, user_id: int) -> List[RatingOut]:
    """Retrieve all ratings submitted by a user with movie details."""
    rows = crud.get_user_ratings(db, user_id)
    results = []
    for r in rows:
        m = _get_movie_info(r['movie_id'])
        if m:
            results.append(RatingOut(
                movie_id=r['movie_id'],
                user_id=user_id,
                rating=float(r['rating']),
                title=m.get('title'),
                year=m.get('year'),
                poster_url=m.get('poster_url') or get_poster_url(r['movie_id'], m.get('tmdb_id_int')),
                genres_list=m.get('genres_list', []),
                created_at=str(r['created_at'])
            ))
    return results


def toggle_user_like(db: sqlite3.Connection, user_id: int, movie_id: int) -> LikeResponse:
    """Toggle favorite / like state for a movie."""
    movie = _get_movie_info(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {movie_id} does not exist in catalog."
        )

    is_liked, message = crud.toggle_favorite(db, user_id, movie_id)
    return LikeResponse(
        movie_id=movie_id,
        user_id=user_id,
        is_liked=is_liked,
        message=message
    )


def get_user_likes_list(db: sqlite3.Connection, user_id: int) -> List[FavoriteOut]:
    """Retrieve list of favorite/liked movies for user."""
    rows = crud.get_user_favorites(db, user_id)
    results = []
    for r in rows:
        m = _get_movie_info(r['movie_id'])
        if m:
            results.append(FavoriteOut(
                movie_id=r['movie_id'],
                title=m.get('title'),
                year=m.get('year'),
                poster_url=m.get('poster_url') or get_poster_url(r['movie_id'], m.get('tmdb_id_int')),
                genres_list=m.get('genres_list', []),
                created_at=str(r['created_at'])
            ))
    return results


def record_user_watch(db: sqlite3.Connection, user_id: int, movie_id: int) -> WatchResponse:
    """Record that a user watched or opened a movie."""
    movie = _get_movie_info(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {movie_id} does not exist in catalog."
        )

    result = crud.add_watch_history(db, user_id, movie_id)
    return WatchResponse(
        movie_id=movie_id,
        user_id=user_id,
        title=movie.get('title'),
        watched_at=result['watched_at'],
        message="Watch interaction recorded successfully."
    )


def get_user_watch_history_list(db: sqlite3.Connection, user_id: int, limit: int = 50) -> List[HistoryOut]:
    """Retrieve watch history records for a user with movie details."""
    rows = crud.get_user_watch_history(db, user_id, limit=limit)
    results = []
    for r in rows:
        m = _get_movie_info(r['movie_id'])
        if m:
            results.append(HistoryOut(
                movie_id=r['movie_id'],
                title=m.get('title'),
                year=m.get('year'),
                poster_url=m.get('poster_url') or get_poster_url(r['movie_id'], m.get('tmdb_id_int')),
                genres_list=m.get('genres_list', []),
                watched_at=str(r['last_watched'])
            ))
    return results


def get_user_interaction_summary(db: sqlite3.Connection, user_id: int) -> InteractionSummary:
    """Get interaction counts and active recommendation strategy."""
    counts = crud.get_interaction_counts(db, user_id)
    total_ratings = counts['ratings']
    total_favorites = counts['favorites']
    total_history = counts['history']
    total_interactions = counts['total']

    if total_interactions == 0:
        strategy = "COLD_START_POPULARITY"
        badge = "Cold-Start Popularity"
        desc = "No ratings recorded yet. The system serves top critically popular titles with verified review depth."
    elif total_interactions < 5:
        strategy = "HYBRID_TRANSITION"
        badge = f"Adaptive Hybrid ({total_interactions}/5 Ratings)"
        desc = f"Emerging profile: Blending collaborative signals from your {total_interactions} interaction(s) with general popular movies."
    else:
        strategy = "COLLABORATIVE_FILTERING"
        badge = "Personalized Collaborative Filtering"
        desc = f"Mature profile ({total_interactions} interactions): 100% personalized recommendations driven by Item-Item Cosine Similarity."

    return InteractionSummary(
        total_ratings=total_ratings,
        total_favorites=total_favorites,
        total_history=total_history,
        total_interactions=total_interactions,
        active_strategy=strategy,
        strategy_badge=badge,
        strategy_description=desc
    )
