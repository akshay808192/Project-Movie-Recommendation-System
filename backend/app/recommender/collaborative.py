"""
Collaborative Filtering Recommendation Engine
Loads precomputed model artifacts and neighbor graph into memory once.
Generates explainable personalized recommendations using Item-Item Cosine Similarity.
Includes comprehensive error handling for unknown users, insufficient interactions,
missing movies, and empty candidate pools.
"""

import os
import pickle
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Set, Tuple, Union

try:
    from backend.app.utils.helpers import get_poster_url
except ImportError:
    def get_poster_url(mid, tmdb=None):
        return None

# ==============================================================================
# CUSTOM EXCEPTIONS FOR PRECISE ERROR HANDLING
# ==============================================================================
class CollaborativeFilteringError(Exception):
    """Base exception for collaborative filtering module."""
    pass

class UserNotFoundError(CollaborativeFilteringError):
    """Raised when a requested user ID does not exist in the training history or database."""
    def __init__(self, user_id: Union[int, str]):
        self.user_id = user_id
        super().__init__(f"User ID {user_id} was not found in interaction history.")

class InsufficientInteractionsError(CollaborativeFilteringError):
    """Raised when a user has fewer ratings than the required minimum threshold for CF."""
    def __init__(self, user_id: Union[int, str], interaction_count: int, min_required: int = 1):
        self.user_id = user_id
        self.interaction_count = interaction_count
        self.min_required = min_required
        super().__init__(
            f"User ID {user_id} has insufficient interactions ({interaction_count} ratings). "
            f"At least {min_required} positive interaction is required for Collaborative Filtering."
        )

class MissingMovieError(CollaborativeFilteringError):
    """Raised when a specified movie ID is not found in the catalog metadata."""
    def __init__(self, movie_id: int):
        self.movie_id = movie_id
        super().__init__(f"Movie ID {movie_id} does not exist in the movie metadata catalog.")

class EmptyRecommendationsError(CollaborativeFilteringError):
    """Raised when no suitable recommendation candidates can be generated."""
    def __init__(self, reason: str = "All candidate neighbors have already been interacted with."):
        self.reason = reason
        super().__init__(f"No recommendation candidates found: {reason}")


# ==============================================================================
# COLLABORATIVE FILTERING RECOMMENDER CLASS
# ==============================================================================
class CollaborativeFilteringRecommender:
    """
    Production Recommender Engine for Item-Item Collaborative Filtering.
    Loads model artifacts into memory once at initialization.
    Does NOT retrain on API requests.
    """

    def __init__(
        self,
        artifact_path: str = "backend/models/collaborative_model.pkl",
        metadata_path: str = "data/processed/movies_metadata.csv",
        item_neighbors: Optional[Dict[int, List[Tuple[int, float]]]] = None,
        movie_metadata: Optional[Dict[int, dict]] = None
    ):
        self.artifact_path = artifact_path
        self.metadata_path = metadata_path

        # If pre-extracted dictionaries are directly passed
        if item_neighbors is not None and movie_metadata is not None:
            self.item_neighbors = item_neighbors
            self.movie_catalog = movie_metadata
            self.train_user_history = {}
            self.movie_to_idx = {}
            self.idx_to_movie = {}
            return

        # Resolve artifact path fallbacks
        if not os.path.exists(artifact_path):
            alt_art = "ml/models/collaborative_model.pkl"
            if os.path.exists(alt_art):
                artifact_path = alt_art
            else:
                from ml.training.train_collaborative import train_collaborative_model
                train_collaborative_model()

        if not os.path.exists(metadata_path):
            alt_meta = "data/movies_processed.csv"
            if os.path.exists(alt_meta):
                metadata_path = alt_meta
            else:
                from ml.preprocessing.preprocess import run_pipeline
                run_pipeline()

        # 1. Load Serialized Artifacts
        with open(artifact_path, "rb") as f:
            self.artifacts = pickle.load(f)

        self.item_neighbors = self.artifacts.get("item_neighbors", {})
        self.train_user_history = self.artifacts.get("train_user_history", {})
        self.movie_to_idx = self.artifacts.get("movie_to_idx", {})
        self.idx_to_movie = self.artifacts.get("idx_to_movie", {})

        # 2. Load Movie Metadata into Fast Memory Dict
        print(f"Loading Movie Metadata from '{metadata_path}'...")
        movies_df = pd.read_csv(metadata_path)
        self.movie_catalog: Dict[int, dict] = {}

        for _, row in movies_df.iterrows():
            mid = int(row['movieId'])
            # Parse genres
            raw_genres = str(row['genres_joined']) if ('genres_joined' in row and pd.notna(row['genres_joined'])) else str(row.get('genres', ''))
            if '|' in raw_genres:
                genres = [g.strip() for g in raw_genres.split('|') if g.strip()]
            else:
                genres = [g.strip().strip("'\"[]") for g in raw_genres.split(',') if g.strip()]

            tmdb_id = int(row['tmdb_id_int']) if ('tmdb_id_int' in row and pd.notna(row['tmdb_id_int'])) else None
            imdb_id = str(row['imdb_id_str']) if ('imdb_id_str' in row and pd.notna(row['imdb_id_str'])) else None

            self.movie_catalog[mid] = {
                "movieId": mid,
                "title": str(row['title']),
                "clean_title": str(row['clean_title']) if ('clean_title' in row and pd.notna(row['clean_title'])) else str(row['title']),
                "year": int(row['year']) if ('year' in row and pd.notna(row['year'])) else None,
                "genres_list": genres,
                "mean_rating": float(round(row['mean_rating'], 2)) if ('mean_rating' in row and pd.notna(row['mean_rating'])) else 0.0,
                "vote_count": int(row['vote_count']) if ('vote_count' in row and pd.notna(row['vote_count'])) else 0,
                "popularity_score": float(round(row['popularity_score'], 3)) if ('popularity_score' in row and pd.notna(row['popularity_score'])) else 0.0,
                "imdb_id_str": imdb_id,
                "tmdb_id_int": tmdb_id,
                "poster_url": get_poster_url(mid, tmdb_id)
            }

        print(f"CollaborativeFilteringRecommender initialized. Cached {len(self.movie_catalog):,} movies and {len(self.train_user_history):,} training users.")

    def get_movie_metadata(self, movie_id: int) -> dict:
        """Fetch metadata for a single movie with error handling."""
        if movie_id not in self.movie_catalog:
            raise MissingMovieError(movie_id)
        return self.movie_catalog[movie_id]

    def recommend_for_user(
        self,
        user_id: Optional[int] = None,
        user_interactions: Optional[List[Tuple[int, float]]] = None,
        top_n: int = 10,
        min_interactions: int = 1,
        genre_filter: Optional[str] = None,
        exclude_movie_ids: Optional[Union[List[int], Set[int]]] = None,
        raise_on_empty: bool = False
    ) -> List[dict]:
        """
        Generate personalized collaborative filtering recommendations.
        
        Args:
            user_id: Integer user ID from dataset training history
            user_interactions: List of explicit (movieId, rating) tuples (e.g. from session or SQLite)
            top_n: Number of recommendations to return
            min_interactions: Minimum interactions required before running CF
            genre_filter: Optional genre string to filter candidate recommendations
            exclude_movie_ids: Optional extra movie IDs to exclude
            raise_on_empty: If True, raises EmptyRecommendationsError when candidates are empty
            
        Returns:
            List of recommended movie dictionaries with scores, match %, and explainability
        """
        # 1. Resolve User Interaction History
        ratings_pool: List[Tuple[int, float]] = []

        if user_interactions is not None:
            ratings_pool = list(user_interactions)
        elif user_id is not None:
            if user_id not in self.train_user_history:
                raise UserNotFoundError(user_id)
            ratings_pool = self.train_user_history[user_id]
        else:
            raise ValueError("Either 'user_id' or 'user_interactions' must be provided.")

        # 2. Check for Insufficient Interactions
        if len(ratings_pool) < min_interactions:
            raise InsufficientInteractionsError(
                user_id=user_id if user_id is not None else "custom_session",
                interaction_count=len(ratings_pool),
                min_required=min_interactions
            )

        # 3. Build Exclusion Set (Exclude all movies the user already rated/interacted with)
        exclude_set = set(exclude_movie_ids or [])
        for mid, _ in ratings_pool:
            exclude_set.add(mid)

        # 4. Weight User Preferences
        # Give higher weight to favorite movies (ratings >= 3.5), baseline weight = (rating - 2.5)
        # Ratings of 5.0 -> weight 2.5; 4.0 -> weight 1.5; 3.0 -> weight 0.5
        preference_weights = {}
        for mid, rating in ratings_pool:
            if mid in self.item_neighbors:
                w = max(0.1, rating - 2.5)
                preference_weights[mid] = max(preference_weights.get(mid, 0.0), w)

        if not preference_weights:
            if raise_on_empty:
                raise EmptyRecommendationsError("None of the user's rated movies exist in the item similarity graph.")
            return []

        # 5. Candidate Accumulation over Item-Item Neighbors
        candidate_scores: Dict[int, float] = {}
        candidate_sources: Dict[int, Tuple[str, float]] = {} # cand_mid -> (source_title, max_sim)

        for source_mid, weight in preference_weights.items():
            neighbors = self.item_neighbors.get(source_mid, [])
            source_meta = self.movie_catalog.get(source_mid)
            source_title = source_meta['clean_title'] if source_meta else f"Movie #{source_mid}"

            for cand_mid, sim in neighbors:
                if cand_mid in exclude_set:
                    continue

                cand_meta = self.movie_catalog.get(cand_mid)
                if not cand_meta:
                    continue

                if genre_filter and genre_filter not in cand_meta.get("genres_list", []):
                    continue

                # Accumulate score: sim * weight
                contribution = sim * weight
                candidate_scores[cand_mid] = candidate_scores.get(cand_mid, 0.0) + contribution

                # Track best single source connection for transparent explanation
                if cand_mid not in candidate_sources or sim > candidate_sources[cand_mid][1]:
                    candidate_sources[cand_mid] = (source_title, sim)

        # 6. Check for Empty Candidate Pool
        if not candidate_scores:
            if raise_on_empty:
                raise EmptyRecommendationsError("All neighboring items are either already consumed or filtered out.")
            return []

        # 7. Sort Candidates by Total CF Score Descending
        ranked_cands = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)

        # 8. Format Recommendations with Full Metadata and Match Percentage
        recommendations = []
        max_cf_score = ranked_cands[0][1] if ranked_cands else 1.0

        for cand_mid, cf_score in ranked_cands[:top_n]:
            meta = self.movie_catalog[cand_mid]
            source_title, best_sim = candidate_sources.get(cand_mid, ("a movie you enjoyed", 0.0))

            # Normalized match percentage between 80% and 99%
            norm_ratio = cf_score / max_cf_score if max_cf_score > 0 else 0.5
            match_pct = int(82 + (norm_ratio * 17))
            match_pct = min(99, max(80, match_pct))

            sim_pct = int(best_sim * 100)
            explanation = (
                f"Personalized: Recommended because you rated '{source_title}' "
                f"({sim_pct}% preference pattern similarity)"
            )

            rec_item = {
                **meta,
                "cf_score": float(round(cf_score, 4)),
                "match_percentage": match_pct,
                "explanation": explanation,
                "source_movie": source_title,
                "similarity_to_source": float(round(best_sim, 4)),
                "recommendation_type": "collaborative_filtering"
            }
            recommendations.append(rec_item)

        return recommendations

    def recommend(
        self,
        user_ratings: Optional[List[Tuple[int, float]]] = None,
        user_favorites: Optional[List[int]] = None,
        exclude_mids: Optional[Set[int]] = None,
        genre: Optional[str] = None,
        top_n: int = 20,
        user_id: Optional[int] = None
    ) -> List[dict]:
        """Convenience alias for hybrid and engine integrations."""
        interactions = list(user_ratings or [])
        if user_favorites:
            for mid in user_favorites:
                interactions.append((mid, 5.0))
        return self.recommend_for_user(
            user_id=user_id,
            user_interactions=interactions if interactions else None,
            top_n=top_n,
            genre_filter=genre,
            exclude_movie_ids=exclude_mids,
            raise_on_empty=False
        )


# ==============================================================================
# GLOBAL SINGLETON INSTANCE & CONVENIENCE FUNCTIONS
# ==============================================================================
_COLLABORATIVE_RECOMMENDER_INSTANCE = None

def get_collaborative_recommender() -> CollaborativeFilteringRecommender:
    """Return singleton instance of CollaborativeFilteringRecommender."""
    global _COLLABORATIVE_RECOMMENDER_INSTANCE
    if _COLLABORATIVE_RECOMMENDER_INSTANCE is None:
        _COLLABORATIVE_RECOMMENDER_INSTANCE = CollaborativeFilteringRecommender()
    return _COLLABORATIVE_RECOMMENDER_INSTANCE

def recommend_for_user(
    user_id: Optional[int] = None,
    user_interactions: Optional[List[Tuple[int, float]]] = None,
    top_n: int = 10,
    genre_filter: Optional[str] = None,
    exclude_movie_ids: Optional[Union[List[int], Set[int]]] = None
) -> List[dict]:
    """
    Top-level functional interface to generate recommendations for a user.
    """
    recommender = get_collaborative_recommender()
    return recommender.recommend_for_user(
        user_id=user_id,
        user_interactions=user_interactions,
        top_n=top_n,
        genre_filter=genre_filter,
        exclude_movie_ids=exclude_movie_ids
    )

if __name__ == "__main__":
    recommender = get_collaborative_recommender()
    print("=" * 80)
    print("TESTING COLLABORATIVE FILTERING RECOMMENDER MODULE")
    print("=" * 80)

    # Test with real dataset User 1
    test_user_id = 1
    print(f"\nGenerating Top 5 Recommendations for User {test_user_id}:")
    try:
        recs = recommender.recommend_for_user(user_id=test_user_id, top_n=5)
        for i, r in enumerate(recs, 1):
            print(f"{i}. {r['clean_title']} ({r['year']}) | CF Score: {r['cf_score']} | Match: {r['match_percentage']}%")
            print(f"   Explanation: {r['explanation']}")
    except CollaborativeFilteringError as e:
        print("Error:", e)
