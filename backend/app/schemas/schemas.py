"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Any


# ==============================================================================
# Authentication & User Schemas
# ==============================================================================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: str = Field(..., min_length=5, max_length=100, description="Valid email address")
    password: str = Field(..., min_length=6, description="Password (at least 6 characters)")


class UserLogin(BaseModel):
    username_or_email: Optional[str] = Field(None, description="Username or email identifier")
    username: Optional[str] = Field(None, description="Username identifier")
    email: Optional[str] = Field(None, description="Email identifier")
    password: str = Field(..., min_length=1, description="Account password")

    @model_validator(mode="after")
    def validate_identifier(self):
        if not (self.username_or_email or self.username or self.email):
            raise ValueError("Must provide username, email, or username_or_email.")
        return self

    @property
    def identifier(self) -> str:
        return (self.username or self.email or self.username_or_email or "").strip()


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ==============================================================================
# Movie Schemas
# ==============================================================================

class MovieBase(BaseModel):
    movieId: int
    title: str
    clean_title: str
    year: Optional[int] = None
    genres_list: List[str] = []
    vote_count: int = 0
    mean_rating: float = 0.0
    popularity_score: float = 0.0
    imdb_id_str: Optional[str] = None
    tmdb_id_int: Optional[int] = None
    poster_url: Optional[str] = None


class MovieDetailOut(MovieBase):
    tags_list: List[str] = []
    user_rating: Optional[float] = None
    is_favorite: bool = False
    in_history: bool = False
    similar_movies: List[MovieBase] = []


class MovieListResponse(BaseModel):
    movies: List[MovieBase]
    total: int
    page: int
    limit: int
    has_next: bool


# ==============================================================================
# Interaction Schemas (Rating, Like/Favorite, Watch History)
# ==============================================================================

class RatingCreate(BaseModel):
    user_id: Optional[int] = Field(None, description="User ID (optional if authenticated with Bearer token)")
    movie_id: int = Field(..., description="ID of the movie being rated")
    rating: float = Field(..., ge=0.5, le=5.0, description="Rating score between 0.5 and 5.0")


class RatingOut(BaseModel):
    movie_id: int
    rating: float
    user_id: Optional[int] = None
    title: Optional[str] = None
    year: Optional[int] = None
    poster_url: Optional[str] = None
    genres_list: List[str] = []
    created_at: Optional[str] = None


class LikeCreate(BaseModel):
    user_id: Optional[int] = Field(None, description="User ID (optional if authenticated with Bearer token)")
    movie_id: int = Field(..., description="ID of the movie to like or favorite")


FavoriteCreate = LikeCreate


class LikeResponse(BaseModel):
    movie_id: int
    user_id: int
    is_liked: bool
    message: str


class FavoriteOut(BaseModel):
    movie_id: int
    title: Optional[str] = None
    year: Optional[int] = None
    poster_url: Optional[str] = None
    genres_list: List[str] = []
    created_at: Optional[str] = None


class WatchCreate(BaseModel):
    user_id: Optional[int] = Field(None, description="User ID (optional if authenticated with Bearer token)")
    movie_id: int = Field(..., description="ID of the movie watched")


HistoryCreate = WatchCreate


class WatchResponse(BaseModel):
    movie_id: int
    user_id: int
    title: Optional[str] = None
    watched_at: str
    message: str


class HistoryOut(BaseModel):
    movie_id: int
    title: Optional[str] = None
    year: Optional[int] = None
    poster_url: Optional[str] = None
    genres_list: List[str] = []
    watched_at: Optional[str] = None


class InteractionSummary(BaseModel):
    total_ratings: int
    total_favorites: int
    total_history: int
    total_interactions: int
    active_strategy: str
    strategy_badge: str
    strategy_description: str


# ==============================================================================
# Recommendation Schemas
# ==============================================================================

class RecommendationItem(MovieBase):
    cf_score: Optional[float] = None
    recommendation_score: Optional[float] = None
    strategy_used: Optional[str] = None
    match_percentage: int = 85
    explanation: str = "Recommended for you"
    source_movie_title: Optional[str] = None


class RecommendationResponse(BaseModel):
    strategy: str
    strategy_badge: str
    strategy_description: str
    user_interaction_count: int
    recommendations: List[RecommendationItem]


# ==============================================================================
# Demo Seed Schema
# ==============================================================================

class SeedDemoRequest(BaseModel):
    taste_profile: str = "action_scifi"  # Options: action_scifi, drama_crime, comedy_animation, romance
