"""
User Interaction Endpoints
Handles Ratings, Likes/Favorites, Watch Events, and Strategy Statistics.
"""

import sqlite3
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path

from backend.app.database.connection import get_db
from backend.app.schemas.schemas import (
    UserOut, RatingCreate, RatingOut, LikeCreate, LikeResponse,
    WatchCreate, WatchResponse, FavoriteOut, HistoryOut, InteractionSummary
)
from backend.app.services.auth_service import get_optional_user, get_current_user
from backend.app.services.interaction_service import (
    submit_rating, delete_user_rating, get_user_ratings_list,
    toggle_user_like, get_user_likes_list,
    record_user_watch, get_user_watch_history_list,
    get_user_interaction_summary
)
from backend.app.database import crud

router = APIRouter(prefix="/interactions", tags=["Interactions"])


def _resolve_user_id(
    data_user_id: Optional[int],
    current_user: Optional[UserOut]
) -> int:
    """
    Resolve target user_id from either the Bearer token or request body.
    """
    if current_user:
        return current_user.id
    if data_user_id is not None:
        return data_user_id
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User authentication token or user_id in payload is required."
    )


# ==============================================================================
# Rating Endpoints
# ==============================================================================

@router.post("/rating", response_model=RatingOut)
def record_rating(
    data: RatingCreate,
    current_user: Optional[UserOut] = Depends(get_optional_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Submit or update a movie rating (0.5 to 5.0).
    Accepts Bearer token or explicit user_id in payload.
    """
    target_user_id = _resolve_user_id(data.user_id, current_user)
    return submit_rating(db, user_id=target_user_id, movie_id=data.movie_id, rating=data.rating)


@router.post("/rate", response_model=RatingOut)
def rate_movie_alias(
    data: RatingCreate,
    current_user: Optional[UserOut] = Depends(get_optional_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """Alias for POST /api/interactions/rating."""
    target_user_id = _resolve_user_id(data.user_id, current_user)
    return submit_rating(db, user_id=target_user_id, movie_id=data.movie_id, rating=data.rating)


@router.delete("/rate/{movie_id}")
def delete_rating(
    movie_id: int = Path(..., description="ID of the movie to delete rating for"),
    current_user: UserOut = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """Delete a user's rating for a movie."""
    return delete_user_rating(db, user_id=current_user.id, movie_id=movie_id)


@router.get("/ratings", response_model=List[RatingOut])
def get_user_ratings(
    current_user: UserOut = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """List all movies rated by the authenticated user."""
    return get_user_ratings_list(db, user_id=current_user.id)


# ==============================================================================
# Like / Favorite Endpoints
# ==============================================================================

@router.post("/like", response_model=LikeResponse)
def like_movie(
    data: LikeCreate,
    current_user: Optional[UserOut] = Depends(get_optional_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Toggle like/favorite status for a movie.
    Accepts Bearer token or explicit user_id in payload.
    """
    target_user_id = _resolve_user_id(data.user_id, current_user)
    return toggle_user_like(db, user_id=target_user_id, movie_id=data.movie_id)


@router.post("/favorite", response_model=LikeResponse)
def favorite_movie_alias(
    data: LikeCreate,
    current_user: Optional[UserOut] = Depends(get_optional_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """Alias for POST /api/interactions/like."""
    target_user_id = _resolve_user_id(data.user_id, current_user)
    return toggle_user_like(db, user_id=target_user_id, movie_id=data.movie_id)


@router.get("/favorites", response_model=List[FavoriteOut])
def get_user_favorites(
    current_user: UserOut = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """List all movies favorited/liked by the authenticated user."""
    return get_user_likes_list(db, user_id=current_user.id)


# ==============================================================================
# Watch History Endpoints
# ==============================================================================

@router.post("/watch", response_model=WatchResponse)
def record_watch(
    data: WatchCreate,
    current_user: Optional[UserOut] = Depends(get_optional_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Record that a user watched or opened a movie.
    Accepts Bearer token or explicit user_id in payload.
    """
    target_user_id = _resolve_user_id(data.user_id, current_user)
    return record_user_watch(db, user_id=target_user_id, movie_id=data.movie_id)


@router.post("/history", response_model=WatchResponse)
def record_history_alias(
    data: WatchCreate,
    current_user: Optional[UserOut] = Depends(get_optional_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """Alias for POST /api/interactions/watch."""
    target_user_id = _resolve_user_id(data.user_id, current_user)
    return record_user_watch(db, user_id=target_user_id, movie_id=data.movie_id)


@router.get("/history", response_model=List[HistoryOut])
def get_watch_history(
    current_user: UserOut = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """Retrieve watch history for the authenticated user."""
    return get_user_watch_history_list(db, user_id=current_user.id)


# ==============================================================================
# Interaction Summary
# ==============================================================================

@router.get("/summary", response_model=InteractionSummary)
def get_interaction_summary(
    current_user: UserOut = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get interaction statistics and active recommendation strategy for current user.
    """
    return get_user_interaction_summary(db, user_id=current_user.id)
