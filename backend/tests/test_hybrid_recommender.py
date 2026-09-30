"""
Unit Tests for Final Hybrid Recommendation Engine (backend/app/recommender/recommender.py)
Tests 3-tier routing (Cold-Start Popularity -> Adaptive Hybrid -> Collaborative Filtering),
configurable thresholds, deduplication, and exclusion of already interacted movies.
"""

import unittest
from backend.app.recommender.recommender import (
    HybridRecommenderEngine,
    get_hybrid_engine,
    recommend_for_user
)

class TestHybridRecommenderEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = get_hybrid_engine()

    def test_case1_zero_interactions_returns_popularity(self):
        """Case 1: User with 0 interactions must receive popularity recommendations."""
        res = self.engine.recommend_for_user(user_interactions=[], limit=10)
        self.assertEqual(res["strategy"], "popularity")
        self.assertEqual(res["user_interaction_count"], 0)
        self.assertEqual(len(res["recommendations"]), 10)

        for rec in res["recommendations"]:
            self.assertIn("movieId", rec)
            self.assertIn("recommendation_score", rec)
            self.assertEqual(rec["strategy_used"], "popularity")

    def test_case2_small_interactions_returns_hybrid(self):
        """Case 2: User with 1-4 interactions must receive hybrid recommendations."""
        # 2 ratings (Godfather mid=858, Goodfellas mid=1213)
        sample_ratings = [(858, 5.0), (1213, 5.0)]
        res = self.engine.recommend_for_user(user_interactions=sample_ratings, limit=10)

        self.assertEqual(res["strategy"], "hybrid")
        self.assertEqual(res["user_interaction_count"], 2)
        self.assertEqual(len(res["recommendations"]), 10)
        self.assertIn("Adaptive Hybrid", res["strategy_badge"])

        # Check deduplication
        returned_ids = [r["movieId"] for r in res["recommendations"]]
        self.assertEqual(len(returned_ids), len(set(returned_ids)), "Recommendations must have no duplicate movie IDs")

        # Check exclusion of interacted movies
        self.assertNotIn(858, returned_ids, "Interacted movie (858) must be excluded")
        self.assertNotIn(1213, returned_ids, "Interacted movie (1213) must be excluded")

    def test_case3_mature_interactions_returns_collaborative(self):
        """Case 3: User with >= 5 interactions must receive collaborative recommendations."""
        # 5 ratings: Star Wars franchise & classic sci-fi
        sample_ratings = [
            (260, 5.0),   # Star Wars: Episode IV
            (1196, 5.0),  # Star Wars: Episode V
            (1210, 5.0),  # Star Wars: Episode VI
            (2571, 5.0),  # Matrix, The
            (589, 4.5)    # Terminator 2
        ]
        res = self.engine.recommend_for_user(user_interactions=sample_ratings, limit=10)

        self.assertEqual(res["strategy"], "collaborative")
        self.assertEqual(res["user_interaction_count"], 5)
        self.assertEqual(len(res["recommendations"]), 10)
        self.assertIn("Collaborative Filtering", res["strategy_badge"])

        # Excluded items check
        returned_ids = [r["movieId"] for r in res["recommendations"]]
        for mid, _ in sample_ratings:
            self.assertNotIn(mid, returned_ids, f"Movie {mid} was interacted with but returned")

    def test_dataset_user_id_collaborative(self):
        """Test that passing a known dataset user_id (User 1) activates collaborative mode."""
        res = self.engine.recommend_for_user(user_id=1, limit=5)
        self.assertEqual(res["strategy"], "collaborative")
        self.assertGreater(res["user_interaction_count"], 20)
        self.assertEqual(len(res["recommendations"]), 5)

    def test_configurable_thresholds(self):
        """Test custom threshold configuration."""
        custom_engine = HybridRecommenderEngine(
            new_user_threshold=0,
            mature_user_threshold=2 # Threshold lowered to 2
        )
        # 2 ratings with custom engine should trigger collaborative instead of hybrid
        res = custom_engine.recommend_for_user(
            user_interactions=[(858, 5.0), (1213, 5.0)],
            limit=5
        )
        self.assertEqual(res["strategy"], "collaborative")

    def test_genre_filtering_across_modes(self):
        """Test genre filtering works properly in hybrid mode."""
        res = self.engine.recommend_for_user(
            user_interactions=[(858, 5.0)],
            genre="Crime",
            limit=5
        )
        self.assertEqual(len(res["recommendations"]), 5)
        for r in res["recommendations"]:
            self.assertIn("Crime", r["genres_list"])

    def test_functional_recommend_for_user(self):
        """Test top-level functional interface recommend_for_user()."""
        res = recommend_for_user(user_interactions=[], limit=4)
        self.assertIn("strategy", res)
        self.assertIn("recommendations", res)
        self.assertEqual(len(res["recommendations"]), 4)

if __name__ == "__main__":
    unittest.main()
