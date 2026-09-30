"""
Final Hybrid Recommendation Engine
Orchestrates Cold-Start Popularity, Adaptive Hybrid Blending, and Personalized Collaborative Filtering.
Completely decoupled from FastAPI for standalone execution and unit testing.
"""

import os
import sys

# Ensure project root is in sys.path for standalone script execution
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import List, Dict, Optional, Set, Tuple, Union, Any

from backend.app.recommender.popularity import (
    PopularityRecommender,
    get_recommender_instance as get_popularity_instance
)
from backend.app.recommender.collaborative import (
    CollaborativeFilteringRecommender,
    get_collaborative_recommender,
    CollaborativeFilteringError,
    UserNotFoundError
)

class HybridRecommenderEngine:
    """
    Unified Recommendation Engine implementing 3-tier routing:
    - CASE 1: New user (0 interactions) -> Popularity Recommender (Bayesian WR)
    - CASE 2: Sparse user (1-4 interactions) -> Adaptive Hybrid (CF + Popularity coverage backfill)
    - CASE 3: Mature user (>=5 interactions) -> Personalized Collaborative Filtering
    """

    def __init__(
        self,
        new_user_threshold: int = 0,
        mature_user_threshold: int = 5,
        popularity_recommender: Optional[PopularityRecommender] = None,
        collaborative_recommender: Optional[CollaborativeFilteringRecommender] = None
    ):
        self.new_user_threshold = new_user_threshold
        self.mature_user_threshold = mature_user_threshold

        self.popularity = popularity_recommender or get_popularity_instance()
        self.collaborative = collaborative_recommender or get_collaborative_recommender()

    def get_user_interaction_history(
        self,
        user_id: Optional[int] = None,
        user_interactions: Optional[List[Tuple[int, float]]] = None
    ) -> List[Tuple[int, float]]:
        """
        Extract interaction history as list of (movieId, rating) tuples.
        """
        if user_interactions is not None:
            return list(user_interactions)

        if user_id is not None:
            # Check training user history
            if user_id in self.collaborative.train_user_history:
                return self.collaborative.train_user_history[user_id]
            # Unknown user with no ratings
            return []

        return []

    def recommend_for_user(
        self,
        user_id: Optional[int] = None,
        limit: int = 20,
        user_interactions: Optional[List[Tuple[int, float]]] = None,
        genre: Optional[str] = None,
        exclude_movie_ids: Optional[Union[List[int], Set[int]]] = None,
        exclude_interacted: bool = True
    ) -> Dict[str, Any]:
        """
        Main recommendation entry point.
        
        Args:
            user_id: Integer user ID
            limit: Maximum recommendations to return
            user_interactions: Optional explicit list of (movieId, rating) tuples
            genre: Optional genre filter
            exclude_movie_ids: Extra movie IDs to exclude
            exclude_interacted: If True, never recommends movies already interacted with
            
        Returns:
            Dictionary containing strategy, badge, description, and list of recommended movies
        """
        # 1. Resolve User Interactions
        history = self.get_user_interaction_history(user_id=user_id, user_interactions=user_interactions)
        interaction_count = len(history)

        # 2. Build Strict Exclusion Set
        exclusion_set: Set[int] = set(exclude_movie_ids or [])
        if exclude_interacted:
            for mid, _ in history:
                exclusion_set.add(mid)

        # ======================================================================
        # CASE 1: NEW USER WITH ZERO INTERACTIONS (Cold Start)
        # ======================================================================
        if interaction_count <= self.new_user_threshold:
            recs = self.popularity.get_popular_movies(
                top_n=limit,
                genre=genre,
                exclude_movie_ids=exclusion_set
            )
            # Tag with strategy score
            for r in recs:
                r["recommendation_score"] = r["weighted_rating"]
                r["strategy_used"] = "popularity"

            return {
                "strategy": "popularity",
                "strategy_badge": "Cold-Start Popularity",
                "strategy_description": (
                    "New user with no interaction history. Serving top critically "
                    "acclaimed films using IMDb Bayesian Weighted Rating formula."
                ),
                "user_interaction_count": 0,
                "recommendations": recs
            }

        # ======================================================================
        # CASE 3: MATURE USER WITH SUFFICIENT INTERACTIONS (Collaborative Filtering)
        # ======================================================================
        if interaction_count >= self.mature_user_threshold:
            try:
                cf_recs = self.collaborative.recommend_for_user(
                    user_id=user_id if user_interactions is None else None,
                    user_interactions=history if user_interactions is not None else None,
                    top_n=limit,
                    genre_filter=genre,
                    exclude_movie_ids=exclusion_set,
                    raise_on_empty=False
                )
            except CollaborativeFilteringError:
                cf_recs = []

            # If collaborative filtering produced enough recommendations
            if len(cf_recs) >= limit:
                for r in cf_recs:
                    r["recommendation_score"] = r["cf_score"]
                    r["strategy_used"] = "collaborative"

                return {
                    "strategy": "collaborative",
                    "strategy_badge": "Personalized Collaborative Filtering",
                    "strategy_description": (
                        f"Personalized recommendations generated using Item-to-Item "
                        f"Cosine Similarity based on your {interaction_count} ratings."
                    ),
                    "user_interaction_count": interaction_count,
                    "recommendations": cf_recs[:limit]
                }

            # Backfill with popularity if CF returned fewer than limit (coverage guarantee)
            cf_movie_ids = {r["movieId"] for r in cf_recs}
            combined_exclusions = exclusion_set.union(cf_movie_ids)
            backfill_needed = limit - len(cf_recs)

            pop_backfill = self.popularity.get_popular_movies(
                top_n=backfill_needed,
                genre=genre,
                exclude_movie_ids=combined_exclusions
            )

            for r in cf_recs:
                r["recommendation_score"] = r["cf_score"]
                r["strategy_used"] = "collaborative"

            for r in pop_backfill:
                r["recommendation_score"] = r["weighted_rating"]
                r["strategy_used"] = "popularity_backfill"
                r["explanation"] = f"Popular Pick: Added for catalog diversity ({r['explanation']})"

            final_recs = cf_recs + pop_backfill

            return {
                "strategy": "collaborative",
                "strategy_badge": "Personalized Collaborative Filtering",
                "strategy_description": (
                    f"Personalized recommendations from your {interaction_count} ratings "
                    f"with popularity coverage support."
                ),
                "user_interaction_count": interaction_count,
                "recommendations": final_recs[:limit]
            }

        # ======================================================================
        # CASE 2: SMALL NUMBER OF INTERACTIONS (Adaptive Hybrid Transition)
        # ======================================================================
        # User has between 1 and (mature_user_threshold - 1) interactions
        alpha = interaction_count / float(self.mature_user_threshold) # e.g. 0.2, 0.4, 0.6, 0.8

        # 1. Fetch CF candidates (requesting double limit for diversity)
        try:
            cf_cands = self.collaborative.recommend_for_user(
                user_id=user_id if user_interactions is None else None,
                user_interactions=history if user_interactions is not None else None,
                top_n=limit * 2,
                genre_filter=genre,
                exclude_movie_ids=exclusion_set,
                raise_on_empty=False
            )
        except CollaborativeFilteringError:
            cf_cands = []

        # 2. Fetch Popularity candidates
        pop_cands = self.popularity.get_popular_movies(
            top_n=limit * 2,
            genre=genre,
            exclude_movie_ids=exclusion_set
        )

        # Normalize CF scores to [0, 1]
        max_cf = max((r["cf_score"] for r in cf_cands), default=1.0)
        if max_cf <= 0:
            max_cf = 1.0

        cf_lookup = {
            r["movieId"]: {
                "norm_score": r["cf_score"] / max_cf,
                "item": r
            }
            for r in cf_cands
        }

        # Normalize Popularity scores to [0, 1] (max WR is ~4.4)
        pop_lookup = {
            r["movieId"]: {
                "norm_score": min(1.0, r["weighted_rating"] / 4.4),
                "item": r
            }
            for r in pop_cands
        }

        # Combine candidate IDs uniquely
        all_candidate_ids = list(dict.fromkeys(list(cf_lookup.keys()) + list(pop_lookup.keys())))
        blended_results = []

        for mid in all_candidate_ids:
            cf_data = cf_lookup.get(mid)
            pop_data = pop_lookup.get(mid)

            cf_norm = cf_data["norm_score"] if cf_data else 0.0
            pop_norm = pop_data["norm_score"] if pop_data else 0.0

            # Alpha blend score
            blend_score = (alpha * cf_norm) + ((1.0 - alpha) * pop_norm)

            if cf_data:
                base_item = dict(cf_data["item"])
                source = base_item.get("source_movie", "a movie you rated")
                expl = (
                    f"Hybrid Pick: {int(alpha*100)}% based on your rating of '{source}' + "
                    f"{int((1-alpha)*100)}% community popularity"
                )
            else:
                base_item = dict(pop_data["item"])
                expl = "Hybrid Pick: Critically popular title matching your emerging taste profile"

            match_pct = min(98, max(78, int(80 + (blend_score * 18))))

            base_item["recommendation_score"] = float(round(blend_score, 4))
            base_item["match_percentage"] = match_pct
            base_item["explanation"] = expl
            base_item["strategy_used"] = "hybrid"

            blended_results.append(base_item)

        # Sort by blended score descending
        blended_results.sort(key=lambda x: x["recommendation_score"], reverse=True)
        final_recs = blended_results[:limit]

        return {
            "strategy": "hybrid",
            "strategy_badge": f"Adaptive Hybrid ({int(alpha*100)}% CF / {int((1-alpha)*100)}% Pop)",
            "strategy_description": (
                f"Emerging profile with {interaction_count} interaction(s). Blending personalized "
                f"collaborative signals from recent ratings with community favorites."
            ),
            "user_interaction_count": interaction_count,
            "recommendations": final_recs
        }


# ==============================================================================
# GLOBAL SINGLETON INSTANCE & FUNCTIONAL API
# ==============================================================================
_HYBRID_ENGINE_INSTANCE = None

def get_hybrid_engine() -> HybridRecommenderEngine:
    global _HYBRID_ENGINE_INSTANCE
    if _HYBRID_ENGINE_INSTANCE is None:
        _HYBRID_ENGINE_INSTANCE = HybridRecommenderEngine()
    return _HYBRID_ENGINE_INSTANCE

def recommend_for_user(
    user_id: Optional[int] = None,
    limit: int = 20,
    user_interactions: Optional[List[Tuple[int, float]]] = None,
    genre: Optional[str] = None,
    exclude_movie_ids: Optional[Union[List[int], Set[int]]] = None,
    exclude_interacted: bool = True
) -> Dict[str, Any]:
    """
    Main functional recommendation endpoint.
    Automatically determines strategy (popularity, hybrid, collaborative).
    """
    engine = get_hybrid_engine()
    return engine.recommend_for_user(
        user_id=user_id,
        limit=limit,
        user_interactions=user_interactions,
        genre=genre,
        exclude_movie_ids=exclude_movie_ids,
        exclude_interacted=exclude_interacted
    )

if __name__ == "__main__":
    engine = get_hybrid_engine()
    print("=" * 80)
    print("TESTING HYBRID RECOMMENDATION ENGINE (recommender.py)")
    print("=" * 80)

    # 1. Test CASE 1: Zero interactions (New User)
    print("\n--- CASE 1: New User with 0 Interactions ---")
    res_cold = engine.recommend_for_user(user_interactions=[], limit=3)
    print(f"Strategy: {res_cold['strategy']} | Badge: {res_cold['strategy_badge']}")
    for i, r in enumerate(res_cold['recommendations'], 1):
        print(f" {i}. {r['clean_title']} ({r['year']}) | Score: {r['recommendation_score']}")

    # 2. Test CASE 2: Small interactions (e.g. 2 ratings -> Hybrid)
    print("\n--- CASE 2: User with 2 Ratings (Adaptive Hybrid) ---")
    small_ratings = [(858, 5.0), (1213, 5.0)] # Godfather, Goodfellas
    res_hybrid = engine.recommend_for_user(user_interactions=small_ratings, limit=3)
    print(f"Strategy: {res_hybrid['strategy']} | Badge: {res_hybrid['strategy_badge']}")
    for i, r in enumerate(res_hybrid['recommendations'], 1):
        print(f" {i}. {r['clean_title']} ({r['year']}) | Score: {r['recommendation_score']} | {r['explanation']}")

    # 3. Test CASE 3: Sufficient interactions (e.g. User 1 in dataset with 232 ratings -> Collaborative)
    print("\n--- CASE 3: Mature User (User 1) ---")
    res_cf = engine.recommend_for_user(user_id=1, limit=3)
    print(f"Strategy: {res_cf['strategy']} | Badge: {res_cf['strategy_badge']}")
    for i, r in enumerate(res_cf['recommendations'], 1):
        print(f" {i}. {r['clean_title']} ({r['year']}) | Score: {r['recommendation_score']} | {r['explanation']}")
