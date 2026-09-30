"""
Recommendation Service
Coordinates recommendation strategies between SQLite user activity and ML recommender modules.
Keeps business logic decoupled from API routers.
"""

import sqlite3
from typing import Optional, List, Dict, Any, Tuple

from backend.app.database import crud
from backend.app.schemas.schemas import (
    RecommendationResponse, RecommendationItem
)
from backend.app.recommender.recommender import (
    HybridRecommenderEngine,
    get_popularity_instance,
    get_collaborative_recommender
)
from backend.app.utils.helpers import get_poster_url

# Singleton instance of HybridRecommenderEngine
_hybrid_engine: Optional[HybridRecommenderEngine] = None


def get_engine() -> HybridRecommenderEngine:
    """Lazy loader for HybridRecommenderEngine singleton."""
    global _hybrid_engine
    if _hybrid_engine is None:
        _hybrid_engine = HybridRecommenderEngine()
    return _hybrid_engine


def get_cold_start_recommendations(
    genre: Optional[str] = None,
    limit: int = 20
) -> RecommendationResponse:
    """
    Generate cold-start recommendations for a new user with zero interactions.
    Strictly uses Bayesian Weighted Rating popularity formula.
    """
    engine = get_engine()
    result = engine.recommend_for_user(
        user_id=None,
        limit=limit,
        user_interactions=[],
        genre=genre,
        exclude_movie_ids=None,
        exclude_interacted=True
    )

    items = []
    for r in result['recommendations']:
        items.append(RecommendationItem(
            movieId=r['movieId'],
            title=r['title'],
            clean_title=r.get('clean_title', r['title']),
            year=r.get('year'),
            genres_list=r.get('genres_list', []),
            vote_count=r.get('vote_count', 0),
            mean_rating=r.get('mean_rating', 0.0),
            popularity_score=r.get('popularity_score', 0.0),
            imdb_id_str=r.get('imdb_id_str'),
            tmdb_id_int=r.get('tmdb_id_int'),
            poster_url=r.get('poster_url') or get_poster_url(r['movieId'], r.get('tmdb_id_int')),
            cf_score=r.get('cf_score'),
            recommendation_score=r.get('recommendation_score'),
            strategy_used=r.get('strategy_used', 'popularity'),
            match_percentage=r.get('match_percentage', 85),
            explanation=r.get('explanation', 'Popular recommendation for new visitors'),
            source_movie_title=r.get('source_movie_title')
        ))

    return RecommendationResponse(
        strategy=result['strategy'],
        strategy_badge=result['strategy_badge'],
        strategy_description=result['strategy_description'],
        user_interaction_count=0,
        recommendations=items
    )


def get_recommendations_for_user(
    user_id: int,
    db: sqlite3.Connection,
    genre: Optional[str] = None,
    limit: int = 20
) -> RecommendationResponse:
    """
    Generate recommendations for an existing user using the hybrid recommendation engine.
    - Resolves interaction history from SQLite database (ratings, favorites, history).
    - If the user has no DB ratings, checks if user_id is in the original training dataset.
    - Decides automatically:
        0 ratings: popularity
        1-4 ratings: adaptive hybrid
        5+ ratings: personalized item-item collaborative filtering
    - Excludes movies the user has already watched or rated.
    """
    engine = get_engine()

    # 1. Fetch ratings from database
    db_ratings = crud.get_user_ratings(db, user_id)
    user_interactions: Optional[List[Tuple[int, float]]] = None

    if db_ratings:
        user_interactions = [(int(r['movie_id']), float(r['rating'])) for r in db_ratings]
    else:
        user_interactions = []

    # 2. Collect favorites and history to exclude
    db_favorites = crud.get_user_favorites(db, user_id)
    db_history = crud.get_user_watch_history(db, user_id)

    extra_exclusions = set()
    for f in db_favorites:
        extra_exclusions.add(int(f['movie_id']))
    for h in db_history:
        extra_exclusions.add(int(h['movie_id']))

    # 3. Call the Hybrid Recommender Engine
    result = engine.recommend_for_user(
        user_id=None,
        limit=limit,
        user_interactions=user_interactions,
        genre=genre,
        exclude_movie_ids=extra_exclusions,
        exclude_interacted=True
    )

    items = []
    for r in result['recommendations']:
        items.append(RecommendationItem(
            movieId=r['movieId'],
            title=r['title'],
            clean_title=r.get('clean_title', r['title']),
            year=r.get('year'),
            genres_list=r.get('genres_list', []),
            vote_count=r.get('vote_count', 0),
            mean_rating=r.get('mean_rating', 0.0),
            popularity_score=r.get('popularity_score', 0.0),
            imdb_id_str=r.get('imdb_id_str'),
            tmdb_id_int=r.get('tmdb_id_int'),
            poster_url=r.get('poster_url') or get_poster_url(r['movieId'], r.get('tmdb_id_int')),
            cf_score=r.get('cf_score'),
            recommendation_score=r.get('recommendation_score'),
            strategy_used=r.get('strategy_used', result['strategy']),
            match_percentage=r.get('match_percentage', 85),
            explanation=r.get('explanation', 'Personalized pick for you'),
            source_movie_title=r.get('source_movie_title')
        ))

    return RecommendationResponse(
        strategy=result['strategy'],
        strategy_badge=result['strategy_badge'],
        strategy_description=result['strategy_description'],
        user_interaction_count=result['user_interaction_count'],
        recommendations=items
    )
