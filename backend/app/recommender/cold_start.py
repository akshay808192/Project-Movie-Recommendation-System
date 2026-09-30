"""
Popularity-Based Cold-Start Recommendation Algorithm
Calculates non-personalized recommendations for new users using IMDB Weighted Rating formula.
"""

from typing import List, Dict, Set, Optional, Tuple

class ColdStartRecommender:
    def __init__(self, popular_movies_ranked: List[int], genre_popularity: Dict[str, List[int]], movie_metadata: Dict[int, dict]):
        self.popular_movies_ranked = popular_movies_ranked
        self.genre_popularity = genre_popularity
        self.movie_metadata = movie_metadata

    def recommend(
        self,
        exclude_mids: Optional[Set[int]] = None,
        genre: Optional[str] = None,
        top_n: int = 20
    ) -> List[Dict]:
        """
        Generate popularity-based recommendations for cold-start users.
        """
        exclude = exclude_mids or set()
        recommendations = []

        pool = self.popular_movies_ranked
        if genre and genre in self.genre_popularity:
            pool = self.genre_popularity[genre]

        for mid in pool:
            if mid in exclude:
                continue

            movie_info = self.movie_metadata.get(mid)
            if not movie_info:
                continue

            pop_score = movie_info.get('popularity_score', 0.0)
            mean_r = movie_info.get('mean_rating', 0.0)
            votes = movie_info.get('vote_count', 0)

            # Compute match percentage based on popularity score (max WR ~ 4.4 -> 98%)
            match_pct = min(98, max(75, int((pop_score / 4.4) * 98)))

            genre_str = f" in {genre}" if genre else ""
            explanation = f"Critically acclaimed blockbuster{genre_str} with {votes} verified reviews (Weighted Score: {pop_score:.2f})"

            rec_item = {
                **movie_info,
                'cf_score': pop_score,
                'match_percentage': match_pct,
                'explanation': explanation,
                'source_movie_title': None
            }
            recommendations.append(rec_item)

            if len(recommendations) >= top_n:
                break

        return recommendations
