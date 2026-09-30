"""
Recommendation Endpoints
Routes cold-start recommendations for new visitors and personalized recommendations for existing users.
"""

import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, Query, Path

from backend.app.database.connection import get_db
from backend.app.schemas.schemas import (
    RecommendationResponse, UserOut, SeedDemoRequest
)
from backend.app.services.auth_service import get_optional_user, get_current_user
from backend.app.services.recommendation_service import (
    get_cold_start_recommendations,
    get_recommendations_for_user
)
from backend.app.database import crud

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

DEMO_TASTE_PROFILES = {
    "action_scifi": [
        (260, 5.0),   # Star Wars: Episode IV
        (1196, 5.0),  # Star Wars: Episode V
        (2571, 5.0),  # Matrix, The
        (589, 4.5),   # Terminator 2
        (58559, 5.0), # Dark Knight, The
    ],
    "drama_crime": [
        (858, 5.0),   # Godfather, The
        (1221, 5.0),  # Godfather: Part II, The
        (1213, 5.0),  # Goodfellas
        (296, 4.5),   # Pulp Fiction
        (318, 5.0),   # Shawshank Redemption, The
    ],
    "comedy_animation": [
        (1, 5.0),     # Toy Story
        (3114, 5.0),  # Toy Story 2
        (588, 4.5),   # Aladdin
        (231, 4.0),   # Dumb & Dumber
        (356, 5.0),   # Forrest Gump
    ]
}


@router.get("", response_model=RecommendationResponse)
def get_recommendations(
    genre: Optional[str] = Query(None, description="Optional genre filter"),
    limit: int = Query(20, ge=1, le=50, description="Number of recommendations to return")
):
    """
    Cold-start recommendation endpoint for a NEW USER.
    Returns popularity-based recommendations calculated via IMDb Bayesian Weighted Rating formula.
    Guarantees high-confidence, acclaimed recommendations without requiring prior interaction history.
    """
    return get_cold_start_recommendations(genre=genre, limit=limit)


@router.get("/cold-start", response_model=RecommendationResponse)
def get_cold_start_alias(
    genre: Optional[str] = Query(None, description="Optional genre filter"),
    limit: int = Query(20, ge=1, le=50)
):
    """Alias for new user cold-start recommendations."""
    return get_cold_start_recommendations(genre=genre, limit=limit)


@router.get("/me", response_model=RecommendationResponse)
def get_my_recommendations(
    genre: Optional[str] = Query(None, description="Optional genre filter"),
    limit: int = Query(20, ge=1, le=50),
    current_user: Optional[UserOut] = Depends(get_optional_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Context-aware recommendation endpoint for current session.
    If authenticated, automatically routes based on the user's interaction count.
    If guest (unauthenticated), serves cold-start popularity recommendations.
    """
    if current_user:
        return get_recommendations_for_user(user_id=current_user.id, db=db, genre=genre, limit=limit)
    return get_cold_start_recommendations(genre=genre, limit=limit)


@router.get("/{user_id}", response_model=RecommendationResponse)
def get_recommendations_by_user_id(
    user_id: int = Path(..., description="The user ID to generate recommendations for"),
    genre: Optional[str] = Query(None, description="Optional genre filter"),
    limit: int = Query(20, ge=1, le=50, description="Number of recommendations to return"),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Recommendation endpoint for an EXISTING USER.
    Uses the Hybrid Recommendation Engine:
    - 0 interactions: Popularity Cold-Start
    - 1-4 interactions: Adaptive Hybrid Transition (blends CF signals with popularity backfill)
    - >= 5 interactions: Personalized Item-Item Collaborative Filtering
    Strictly excludes movies the user has already rated or watched.
    """
    return get_recommendations_for_user(user_id=user_id, db=db, genre=genre, limit=limit)


@router.post("/demo-seed")
def seed_demo_taste_profile(
    data: SeedDemoRequest,
    current_user: UserOut = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Interactive Demo Helper:
    Seeds 5 realistic ratings into SQLite to transition user to Collaborative Filtering mode.
    """
    profile_key = data.taste_profile if data.taste_profile in DEMO_TASTE_PROFILES else "action_scifi"
    seed_ratings = DEMO_TASTE_PROFILES[profile_key]

    for mid, rating in seed_ratings:
        crud.save_rating(db, current_user.id, mid, rating)

    return {
        "message": f"Successfully seeded '{profile_key}' profile with {len(seed_ratings)} ratings!",
        "seeded_count": len(seed_ratings),
        "status": "ready_for_collaborative_filtering"
    }
