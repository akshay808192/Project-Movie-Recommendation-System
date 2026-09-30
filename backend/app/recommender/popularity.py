"""
Popularity-Based Recommendation Engine
Implements Bayesian Weighted Rating (IMDb formula) to solve the cold-start problem.
Dynamically calculates parameters C and m from the dataset rather than hardcoding.
"""

import os
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Set, Union

try:
    from backend.app.utils.helpers import get_poster_url
except ImportError:
    # Standalone fallback if run directly
    def get_poster_url(mid, tmdb=None):
        return None

class PopularityRecommender:
    """
    Robust Popularity Recommendation System based on Bayesian Weighted Rating.
    
    Formula:
        WR = (v / (v + m)) * R + (m / (v + m)) * C
        
    Where:
        v = Number of reviews/ratings for the movie
        m = Minimum review threshold (dynamically set from quantile of vote counts)
        R = Average rating for the movie
        C = Overall average rating across all movies in the dataset
    """

    def __init__(
        self,
        metadata_path: str = "data/processed/movies_metadata.csv",
        interactions_path: Optional[str] = "data/processed/interactions_clean.csv",
        quantile_threshold: float = 0.80
    ):
        # Resolve data paths with fallbacks
        if not os.path.exists(metadata_path):
            alt_path = "data/movies_processed.csv"
            if os.path.exists(alt_path):
                metadata_path = alt_path
            else:
                # If neither processed exists, fall back to ml/preprocessing
                from ml.preprocessing.preprocess import run_pipeline
                run_pipeline()

        self.metadata_path = metadata_path
        self.quantile_threshold = quantile_threshold
        self.movies_df = pd.read_csv(self.metadata_path)

        # Parse genres if stored as strings
        if 'genres_list' not in self.movies_df.columns or isinstance(self.movies_df['genres_list'].iloc[0], str):
            def parse_genres(val):
                if pd.isna(val) or val == '[]':
                    return []
                if isinstance(val, list):
                    return val
                # Handle pipe-separated or comma/eval
                if '|' in str(val):
                    return [g.strip() for g in str(val).split('|') if g.strip()]
                cleaned = str(val).strip("[]'\" ")
                return [g.strip().strip("'\"") for g in cleaned.split(',') if g.strip()]

            genre_col = 'genres_joined' if 'genres_joined' in self.movies_df.columns else 'genres'
            self.movies_df['genres_list'] = self.movies_df[genre_col].apply(parse_genres)

        # Compute or verify Bayesian Weighted Rating
        self._calculate_dataset_parameters(interactions_path)
        self._build_popularity_indices()

    def _calculate_dataset_parameters(self, interactions_path: Optional[str] = None):
        """
        Dynamically calculate global mean C and minimum vote threshold m from actual data.
        """
        if interactions_path and os.path.exists(interactions_path):
            ratings_df = pd.read_csv(interactions_path)
            self.C = float(ratings_df['rating'].mean())
        elif 'popularity_score' in self.movies_df.columns and 'mean_rating' in self.movies_df.columns:
            # Weighted average across catalog
            total_votes = self.movies_df['vote_count'].sum()
            if total_votes > 0:
                self.C = float((self.movies_df['mean_rating'] * self.movies_df['vote_count']).sum() / total_votes)
            else:
                self.C = 3.5
        else:
            self.C = 3.5

        # Dynamic vote threshold m based on actual quantile
        rated_movies = self.movies_df[self.movies_df['vote_count'] > 0]
        if not rated_movies.empty:
            self.m = float(rated_movies['vote_count'].quantile(self.quantile_threshold))
        else:
            self.m = 10.0

        # Compute or update Weighted Rating column
        def calc_wr(row):
            v = row['vote_count']
            R = row['mean_rating']
            if v == 0:
                return 0.0
            return (v / (v + self.m)) * R + (self.m / (v + self.m)) * self.C

        self.movies_df['weighted_rating'] = self.movies_df.apply(calc_wr, axis=1).round(4)
        self.movies_df['popularity_score'] = self.movies_df['weighted_rating']

    def _build_popularity_indices(self):
        """
        Pre-index overall and genre-specific ranked pools for instant lookups.
        """
        # Overall ranked
        self.ranked_all = self.movies_df.sort_values(by='weighted_rating', ascending=False)

        # Genre-specific pools
        self.genre_pools = {}
        for idx, row in self.movies_df.iterrows():
            genres = row['genres_list']
            for g in genres:
                if g not in self.genre_pools:
                    self.genre_pools[g] = []
                self.genre_pools[g].append(row)

        for g in self.genre_pools:
            pool_df = pd.DataFrame(self.genre_pools[g])
            self.genre_pools[g] = pool_df.sort_values(by='weighted_rating', ascending=False)

        # Pre-build metadata dictionary for O(1) lookups
        self._metadata_dict = {}
        for _, row in self.movies_df.iterrows():
            mid = int(row['movieId'])
            self._metadata_dict[mid] = self._format_movie_output(row)

    def get_movie_metadata(self, movie_id: int) -> Optional[dict]:
        """Fetch metadata dictionary for a specific movie ID (O(1) lookup)."""
        return self._metadata_dict.get(movie_id)

    def _format_movie_output(self, row: pd.Series) -> dict:
        """
        Format a movie record with all metadata required by frontend and API.
        """
        mid = int(row['movieId'])
        tmdb_id = int(row['tmdb_id_int']) if ('tmdb_id_int' in row and pd.notna(row['tmdb_id_int'])) else None
        imdb_id = str(row['imdb_id_str']) if ('imdb_id_str' in row and pd.notna(row['imdb_id_str'])) else None
        
        title = str(row['title'])
        clean_title = str(row['clean_title']) if ('clean_title' in row and pd.notna(row['clean_title'])) else title
        year = int(row['year']) if ('year' in row and pd.notna(row['year'])) else None
        genres = row['genres_list'] if isinstance(row['genres_list'], list) else []

        mean_r = float(round(row['mean_rating'], 2))
        v_count = int(row['vote_count'])
        wr_score = float(round(row['weighted_rating'], 3))

        # Match percentage scaled from Bayesian WR (scale: 75% to 98%)
        match_pct = min(98, max(75, int((wr_score / 4.4) * 98)))

        explanation = (
            f"Popular Choice: Rated {mean_r:.1f}/5 stars across {v_count:,} reviews "
            f"(Bayesian Weighted Score: {wr_score:.2f})"
        )

        return {
            "movieId": mid,
            "title": title,
            "clean_title": clean_title,
            "year": year,
            "genres_list": genres,
            "mean_rating": mean_r,
            "vote_count": v_count,
            "popularity_score": wr_score,
            "weighted_rating": wr_score,
            "match_percentage": match_pct,
            "explanation": explanation,
            "imdb_id_str": imdb_id,
            "tmdb_id_int": tmdb_id,
            "poster_url": get_poster_url(mid, tmdb_id),
            "recommendation_type": "popularity_cold_start"
        }

    def get_popular_movies(
        self,
        top_n: int = 20,
        genre: Optional[str] = None,
        exclude_movie_ids: Optional[Union[List[int], Set[int]]] = None
    ) -> List[dict]:
        """
        Retrieve top-N popular movies, with optional genre filtering and item exclusion.
        """
        exclude_set = set(exclude_movie_ids or [])
        source_df = self.ranked_all

        if genre and genre in self.genre_pools:
            source_df = self.genre_pools[genre]

        results = []
        for _, row in source_df.iterrows():
            mid = int(row['movieId'])
            if mid in exclude_set:
                continue

            results.append(self._format_movie_output(row))
            if len(results) >= top_n:
                break

        return results

    def get_top_movies(
        self,
        top_n: int = 20,
        min_votes: Optional[int] = None,
        exclude_movie_ids: Optional[Union[List[int], Set[int]]] = None
    ) -> List[dict]:
        """
        Retrieve highest-ranked movies satisfying an optional minimum vote constraint.
        """
        exclude_set = set(exclude_movie_ids or [])
        threshold = min_votes if min_votes is not None else int(self.m)

        filtered = self.ranked_all[self.ranked_all['vote_count'] >= threshold]
        results = []

        for _, row in filtered.iterrows():
            mid = int(row['movieId'])
            if mid in exclude_set:
                continue

            results.append(self._format_movie_output(row))
            if len(results) >= top_n:
                break

        return results

    def get_popular_by_genre(
        self,
        genre: str,
        top_n: int = 20,
        exclude_movie_ids: Optional[Union[List[int], Set[int]]] = None
    ) -> List[dict]:
        """
        Retrieve top-N popular movies specifically for a given genre.
        """
        return self.get_popular_movies(
            top_n=top_n,
            genre=genre,
            exclude_movie_ids=exclude_movie_ids
        )


# ==============================================================================
# GLOBAL SINGLETON & FUNCTIONAL API INTERFACE
# ==============================================================================
_POPULARITY_RECOMMENDER_INSTANCE = None

def get_recommender_instance() -> PopularityRecommender:
    global _POPULARITY_RECOMMENDER_INSTANCE
    if _POPULARITY_RECOMMENDER_INSTANCE is None:
        _POPULARITY_RECOMMENDER_INSTANCE = PopularityRecommender()
    return _POPULARITY_RECOMMENDER_INSTANCE

def get_popular_movies(
    top_n: int = 20,
    genre: Optional[str] = None,
    exclude_movie_ids: Optional[Union[List[int], Set[int]]] = None
) -> List[dict]:
    """Functional interface for popular movie recommendations."""
    return get_recommender_instance().get_popular_movies(
        top_n=top_n,
        genre=genre,
        exclude_movie_ids=exclude_movie_ids
    )

def get_top_movies(
    top_n: int = 20,
    min_votes: Optional[int] = None,
    exclude_movie_ids: Optional[Union[List[int], Set[int]]] = None
) -> List[dict]:
    """Functional interface for top movies by weighted rating with min_votes filter."""
    return get_recommender_instance().get_top_movies(
        top_n=top_n,
        min_votes=min_votes,
        exclude_movie_ids=exclude_movie_ids
    )

def get_popular_by_genre(
    genre: str,
    top_n: int = 20,
    exclude_movie_ids: Optional[Union[List[int], Set[int]]] = None
) -> List[dict]:
    """Functional interface for genre-specific popular movies."""
    return get_recommender_instance().get_popular_by_genre(
        genre=genre,
        top_n=top_n,
        exclude_movie_ids=exclude_movie_ids
    )

if __name__ == "__main__":
    recommender = PopularityRecommender()
    print("=" * 70)
    print("TESTING POPULARITY RECOMMENDATION MODULE")
    print(f"Dataset Overall Average Rating (C): {recommender.C:.4f}")
    print(f"Dynamic Minimum Vote Threshold (m): {recommender.m:.1f} votes")
    print("=" * 70)

    print("\n--- TOP 5 OVERALL POPULAR MOVIES (IMDb Bayesian Weighted Rating) ---")
    top_5 = recommender.get_popular_movies(top_n=5)
    for i, m in enumerate(top_5, 1):
        print(f"{i}. {m['clean_title']} ({m['year']}) - WR: {m['weighted_rating']:.2f} | Mean: {m['mean_rating']} stars ({m['vote_count']} votes)")

    print("\n--- TOP 3 POPULAR SCI-FI MOVIES ---")
    scifi_3 = recommender.get_popular_by_genre("Sci-Fi", top_n=3)
    for i, m in enumerate(scifi_3, 1):
        print(f"{i}. {m['clean_title']} ({m['year']}) - WR: {m['weighted_rating']:.2f} | Genres: {m['genres_list']}")
