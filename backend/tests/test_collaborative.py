"""
Unit Tests for Collaborative Filtering Recommendation Module
(backend/app/recommender/collaborative.py)
Tests Item-Item CF logic, exclusion filters, schema integrity, and error handling.
"""

import unittest
from backend.app.recommender.collaborative import (
    CollaborativeFilteringRecommender,
    get_collaborative_recommender,
    recommend_for_user,
    UserNotFoundError,
    InsufficientInteractionsError,
    MissingMovieError,
    EmptyRecommendationsError
)

class TestCollaborativeRecommender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load collaborative model once for all tests."""
        cls.recommender = get_collaborative_recommender()

    def test_recommend_known_user(self):
        """Test recommendations generation for a valid training user (User 1)."""
        recs = self.recommender.recommend_for_user(user_id=1, top_n=5)
        self.assertEqual(len(recs), 5)
        self.assertGreater(recs[0]["cf_score"], 0)
        self.assertGreaterEqual(recs[0]["match_percentage"], 80)
        self.assertLessEqual(recs[0]["match_percentage"], 99)

    def test_exclusion_of_rated_movies(self):
        """Test that movies already rated by the user are strictly excluded."""
        user_1_rated_mids = set(mid for mid, _ in self.recommender.train_user_history[1])
        self.assertGreater(len(user_1_rated_mids), 0)

        recs = self.recommender.recommend_for_user(user_id=1, top_n=20)
        for rec in recs:
            self.assertNotIn(
                rec["movieId"],
                user_1_rated_mids,
                f"Movie {rec['movieId']} ({rec['title']}) was already rated by User 1 but returned in recs"
            )

    def test_output_schema_and_metadata(self):
        """Verify full metadata mapping and presence of explanation strings."""
        recs = self.recommender.recommend_for_user(user_id=1, top_n=5)
        required_keys = [
            "movieId", "title", "clean_title", "year", "genres_list",
            "mean_rating", "vote_count", "popularity_score", "cf_score",
            "match_percentage", "explanation", "source_movie", "recommendation_type"
        ]

        for item in recs:
            for key in required_keys:
                self.assertIn(key, item, f"Key '{key}' missing from collaborative recommendation output")
            self.assertEqual(item["recommendation_type"], "collaborative_filtering")
            self.assertIn("Personalized: Recommended because you rated", item["explanation"])

    def test_unknown_user_raises_error(self):
        """Verify that requesting an unknown user ID raises UserNotFoundError."""
        with self.assertRaises(UserNotFoundError) as ctx:
            self.recommender.recommend_for_user(user_id=999999, top_n=5)
        self.assertIn("999999", str(ctx.exception))

    def test_insufficient_interactions_raises_error(self):
        """Verify that a user with empty interactions raises InsufficientInteractionsError."""
        with self.assertRaises(InsufficientInteractionsError):
            self.recommender.recommend_for_user(
                user_interactions=[],
                top_n=5,
                min_interactions=1
            )

    def test_missing_movie_metadata_error(self):
        """Verify that requesting metadata for a non-existent movie raises MissingMovieError."""
        with self.assertRaises(MissingMovieError):
            self.recommender.get_movie_metadata(movie_id=9999999)

    def test_custom_user_interactions(self):
        """
        Verify dynamic folding-in of new user ratings without retraining.
        Simulate a user who loves Star Wars (Episode IV, V, VI).
        """
        star_wars_ratings = [
            (260, 5.0),   # Star Wars: Episode IV
            (1196, 5.0),  # Star Wars: Episode V
            (1210, 5.0)   # Star Wars: Episode VI
        ]
        recs = self.recommender.recommend_for_user(
            user_interactions=star_wars_ratings,
            top_n=5
        )
        self.assertGreater(len(recs), 0)
        # Should recommend related sci-fi / classic action (e.g. Raiders of the Lost Ark, Terminator, etc.)
        returned_titles = [r["clean_title"] for r in recs]
        self.assertTrue(len(returned_titles) == 5)
        self.assertNotIn("Star Wars: Episode IV - A New Hope", returned_titles)

    def test_genre_filter(self):
        """Verify that genre_filter restricts recommendations to the target genre."""
        recs = self.recommender.recommend_for_user(
            user_id=1,
            top_n=5,
            genre_filter="Sci-Fi"
        )
        self.assertGreater(len(recs), 0)
        for r in recs:
            self.assertIn("Sci-Fi", r["genres_list"])

    def test_empty_candidates_handling(self):
        """Verify that raise_on_empty=True correctly raises EmptyRecommendationsError when impossible."""
        with self.assertRaises(EmptyRecommendationsError):
            self.recommender.recommend_for_user(
                user_interactions=[(1, 5.0)],
                top_n=5,
                genre_filter="NonExistentGenre123",
                raise_on_empty=True
            )

if __name__ == "__main__":
    unittest.main()
