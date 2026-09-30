"""
Recommender Engine Core Singleton
Loads ML artifacts and movie dataset into memory and provides unified recommendation and search services.
"""

import os
import pickle
import pandas as pd
from typing import List, Dict, Optional, Set, Tuple

from backend.app.recommender.cold_start import ColdStartRecommender
from backend.app.recommender.collaborative import CollaborativeFilteringRecommender
from backend.app.recommender.hybrid import HybridRecommender
from backend.app.utils.helpers import get_poster_url

class RecommenderEngine:
    _instance = None

    def __init__(
        self,
        artifact_path: str = "backend/models/recommender_artifacts.pkl",
        movies_path: str = "data/movies_processed.csv"
    ):
        print(f"Loading RecommenderEngine artifacts from '{artifact_path}'...")
        if not os.path.exists(artifact_path):
            artifact_path = "ml/models/recommender_artifacts.pkl"

        with open(artifact_path, 'rb') as f:
            self.artifacts = pickle.load(f)

        print(f"Loading movies from '{movies_path}'...")
        movies_df = pd.read_csv(movies_path)

        # Build in-memory movie metadata dict for sub-millisecond lookup
        self.movie_metadata: Dict[int, dict] = {}
        for _, row in movies_df.iterrows():
            mid = int(row['movieId'])
            raw_genres = str(row['genres_joined']) if pd.notna(row['genres_joined']) else ""
            genres_list = [g.strip() for g in raw_genres.split('|') if g.strip()]
            
            raw_tags = str(row['tags_joined']) if ('tags_joined' in row and pd.notna(row['tags_joined'])) else ""
            tags_list = [t.strip() for t in raw_tags.split('|') if t.strip()]

            tmdb_id = int(row['tmdb_id_int']) if ('tmdb_id_int' in row and pd.notna(row['tmdb_id_int'])) else None

            self.movie_metadata[mid] = {
                'movieId': mid,
                'title': str(row['title']),
                'clean_title': str(row['clean_title']) if 'clean_title' in row else str(row['title']),
                'year': int(row['year']) if ('year' in row and pd.notna(row['year'])) else None,
                'genres_list': genres_list,
                'tags_list': tags_list,
                'vote_count': int(row['vote_count']) if ('vote_count' in row and pd.notna(row['vote_count'])) else 0,
                'mean_rating': float(round(row['mean_rating'], 2)) if ('mean_rating' in row and pd.notna(row['mean_rating'])) else 0.0,
                'popularity_score': float(round(row['popularity_score'], 3)) if ('popularity_score' in row and pd.notna(row['popularity_score'])) else 0.0,
                'imdb_id_str': str(row['imdb_id_str']) if ('imdb_id_str' in row and pd.notna(row['imdb_id_str'])) else None,
                'tmdb_id_int': tmdb_id,
                'poster_url': get_poster_url(mid, tmdb_id)
            }

        # Initialize components
        self.cold_start = ColdStartRecommender(
            popular_movies_ranked=self.artifacts['popular_movies_ranked'],
            genre_popularity=self.artifacts['genre_popularity'],
            movie_metadata=self.movie_metadata
        )

        self.collaborative = CollaborativeFilteringRecommender(
            item_neighbors=self.artifacts['item_neighbors'],
            movie_metadata=self.movie_metadata
        )

        self.hybrid = HybridRecommender(
            cold_start_recommender=self.cold_start,
            collaborative_recommender=self.collaborative,
            movie_metadata=self.movie_metadata
        )

        self.all_genres = sorted(list(self.artifacts['genre_popularity'].keys()))
        print(f"RecommenderEngine loaded {len(self.movie_metadata)} movies across {len(self.all_genres)} genres.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RecommenderEngine()
        return cls._instance

    def get_movie(self, movie_id: int) -> Optional[dict]:
        """Fetch single movie by id."""
        return self.movie_metadata.get(movie_id)

    def get_similar_movies(self, movie_id: int, top_n: int = 10) -> List[dict]:
        """Fetch top item-item collaborative neighbors for a movie."""
        neighbors = self.artifacts['item_neighbors'].get(movie_id, [])
        similar_movies = []
        for cand_mid, sim in neighbors[:top_n]:
            m = self.movie_metadata.get(cand_mid)
            if m:
                similar_movies.append({
                    **m,
                    'cf_score': sim,
                    'match_percentage': int(min(99, max(75, 75 + (sim * 25))))
                })
        return similar_movies

    def get_popular(
        self,
        genre: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[dict], int]:
        """Get popular movies with pagination and optional genre filter."""
        pool = self.artifacts['popular_movies_ranked']
        if genre and genre in self.artifacts['genre_popularity']:
            pool = self.artifacts['genre_popularity'][genre]

        total = len(pool)
        start = (page - 1) * limit
        end = start + limit
        paged_ids = pool[start:end]

        movies = [self.movie_metadata[mid] for mid in paged_ids if mid in self.movie_metadata]
        return movies, total

    def search_movies(
        self,
        query: str = "",
        genre: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[dict], int]:
        """Search movies by title, year, or tags."""
        q = query.strip().lower()
        matched = []

        for mid, m in self.movie_metadata.items():
            if genre and genre not in m['genres_list']:
                continue

            if q:
                title_match = q in m['clean_title'].lower() or q in m['title'].lower()
                year_match = q == str(m['year']) if m['year'] else False
                tag_match = any(q in t for t in m['tags_list'])
                if not (title_match or year_match or tag_match):
                    continue

            matched.append(m)

        # Sort search matches by popularity score descending
        matched.sort(key=lambda x: x['popularity_score'], reverse=True)

        total = len(matched)
        start = (page - 1) * limit
        end = start + limit
        return matched[start:end], total

    def get_recommendations(
        self,
        user_ratings: List[Tuple[int, float]],
        user_favorites: Optional[List[int]] = None,
        user_history: Optional[List[int]] = None,
        genre: Optional[str] = None,
        top_n: int = 20
    ) -> Dict:
        """Route to appropriate strategy and return recommendations."""
        return self.hybrid.recommend(
            user_ratings=user_ratings,
            user_favorites=user_favorites,
            user_history=user_history,
            genre=genre,
            top_n=top_n
        )
