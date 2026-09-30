"""
Movie Endpoints
Handles catalog browsing, search, movie details, and popular titles.
"""

import sqlite3
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path

from backend.app.database.connection import get_db
from backend.app.schemas.schemas import MovieBase, MovieDetailOut, MovieListResponse, UserOut
from backend.app.services.auth_service import get_optional_user
from backend.app.services.movie_service import get_movie_details, list_popular_movies, search_movies
from backend.app.recommender.popularity import get_recommender_instance
from backend.app.recommender.collaborative import get_collaborative_recommender

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("", response_model=MovieListResponse)
def get_movies(
    q: Optional[str] = Query(None, description="Search term for title, year, or tag"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Search and browse catalog movies."""
    return search_movies(query=q or "", genre=genre, page=page, limit=limit)


@router.get("/popular", response_model=MovieListResponse)
def get_popular_movies_endpoint(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Retrieve top critically acclaimed movies based on IMDb Bayesian Weighted Rating formula.
    Ensures high confidence and quality for popular browsing and cold-start discovery.
    """
    return list_popular_movies(genre=genre, page=page, limit=limit)


@router.get("/search", response_model=MovieListResponse)
def search_movies_endpoint(
    query: Optional[str] = Query(None, description="Search term for title, year, or tag"),
    q: Optional[str] = Query(None, description="Alternative alias for search query"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Dedicated movie search endpoint.
    Matches movie title, release year, or descriptive semantic tags.
    """
    search_term = query or q or ""
    return search_movies(query=search_term, genre=genre, page=page, limit=limit)


@router.get("/genres", response_model=List[str])
def get_genres():
    """Retrieve list of all unique movie genres in catalog."""
    pop = get_recommender_instance()
    return pop.all_genres


@router.get("/{movie_id}", response_model=MovieDetailOut)
def get_movie(
    movie_id: int = Path(..., description="The unique ID of the movie"),
    current_user: Optional[UserOut] = Depends(get_optional_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieve complete movie information, similar recommendations, and user interaction state
    (if authenticated).
    """
    return get_movie_details(movie_id=movie_id, db=db, current_user=current_user)


@router.get("/{movie_id}/similar", response_model=List[MovieBase])
def get_similar_movies_endpoint(
    movie_id: int = Path(..., description="The unique ID of the movie"),
    limit: int = Query(10, ge=1, le=50, description="Number of similar movies to return")
):
    """
    Retrieve most similar movies using Item-to-Item Cosine Similarity.
    """
    cf = get_collaborative_recommender()
    sims = cf.get_similar_movies(movie_id, top_n=limit)
    return [MovieBase(**s) for s in sims]
