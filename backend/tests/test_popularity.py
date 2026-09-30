"""
Unit Tests for Popularity Recommendation System (backend/app/recommender/popularity.py)
Tests mathematical validity of Bayesian Weighted Rating, metadata structure,
exclusion filters, genre filtering, and vote thresholds on real dataset.
"""

import unittest
import numpy as np
import pandas as pd
from backend.app.recommender.popularity import (
    PopularityRecommender,
    get_popular_movies,
    get_top_movies,
    get_popular_by_genre
)

class TestPopularityRecommender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize recommender instance once for all tests."""
        cls.recommender = PopularityRecommender(quantile_threshold=0.80)

    def test_dataset_parameters_dynamic(self):
        """Test that C and m are dynamically computed and within expected range."""
        self.assertGreater(self.recommender.C, 3.0)
        self.assertLess(self.recommender.C, 4.0)
        self.assertAlmostEqual(self.recommender.C, 3.5016, places=2)

        # Threshold m is 80th percentile of rated movies (12 votes)
        self.assertGreaterEqual(self.recommender.m, 5.0)
        self.assertLessEqual(self.recommender.m, 25.0)
        self.assertEqual(self.recommender.m, 12.0)

    def test_weighted_rating_penalizes_low_votes(self):
        """
        Verify that Bayesian WR solves the cold-start problem by pulling
        obscure movies with 1 rating towards global mean C, while rewarding
        highly rated movies with large review depth.
        """
        C = self.recommender.C
        m = self.recommender.m

        # Movie A: 1 review of 5.0 stars
        v_a = 1
        R_a = 5.0
        wr_a = (v_a / (v_a + m)) * R_a + (m / (v_a + m)) * C

        # Movie B: 200 reviews of 4.4 stars
        v_b = 200
        R_b = 4.4
        wr_b = (v_b / (v_b + m)) * R_b + (m / (v_b + m)) * C

        # In simple average, Movie A (5.0) > Movie B (4.4).
        # In Bayesian WR, Movie B must rank HIGHER than Movie A!
        self.assertGreater(wr_b, wr_a, "Bayesian WR must rank 200-review movie higher than 1-review 5.0-star movie")
        self.assertLess(wr_a, 4.0, "1-review 5.0 movie must be heavily shrunk towards dataset mean C")

    def test_get_popular_movies_schema(self):
        """Test that get_popular_movies returns valid schemas and required metadata."""
        top_10 = self.recommender.get_popular_movies(top_n=10)
        self.assertEqual(len(top_10), 10)

        required_keys = [
            "movieId", "title", "clean_title", "year", "genres_list",
            "mean_rating", "vote_count", "popularity_score", "weighted_rating",
            "match_percentage", "explanation"
        ]

        for item in top_10:
            for key in required_keys:
                self.assertIn(key, item, f"Key '{key}' missing from movie output")
            self.assertIsInstance(item["movieId"], int)
            self.assertIsInstance(item["genres_list"], list)
            self.assertGreater(item["vote_count"], 0)
            self.assertGreaterEqual(item["match_percentage"], 75)
            self.assertLessEqual(item["match_percentage"], 99)

    def test_get_popular_movies_ordering(self):
        """Test that returned popular movies are sorted strictly descending by weighted rating."""
        movies = self.recommender.get_popular_movies(top_n=20)
        scores = [m["weighted_rating"] for m in movies]
        sorted_scores = sorted(scores, reverse=True)
        self.assertEqual(scores, sorted_scores, "Popular movies must be sorted in descending order of weighted rating")

    def test_exclusion_filter(self):
        """Test that exclude_movie_ids successfully filters out watched/rated movies."""
        top_popular = self.recommender.get_popular_movies(top_n=5)
        excluded_ids = [top_popular[0]["movieId"], top_popular[1]["movieId"]]

        filtered_recs = self.recommender.get_popular_movies(
            top_n=5,
            exclude_movie_ids=excluded_ids
        )
        returned_ids = [m["movieId"] for m in filtered_recs]

        for ex_id in excluded_ids:
            self.assertNotIn(ex_id, returned_ids, f"Excluded movie ID {ex_id} was incorrectly returned")

    def test_get_popular_by_genre(self):
        """Test that genre-specific recommendations strictly contain the requested genre."""
        genres_to_test = ["Action", "Sci-Fi", "Comedy", "Drama", "Animation"]

        for genre in genres_to_test:
            genre_recs = self.recommender.get_popular_by_genre(genre=genre, top_n=5)
            self.assertGreater(len(genre_recs), 0, f"No movies returned for genre {genre}")
            for movie in genre_recs:
                self.assertIn(
                    genre,
                    movie["genres_list"],
                    f"Movie '{movie['title']}' does not contain expected genre '{genre}'"
                )

    def test_get_top_movies_min_votes(self):
        """Test that get_top_movies respects the min_votes constraint."""
        min_v = 50
        top_filtered = self.recommender.get_top_movies(top_n=10, min_votes=min_v)
        self.assertEqual(len(top_filtered), 10)

        for movie in top_filtered:
            self.assertGreaterEqual(
                movie["vote_count"],
                min_v,
                f"Movie '{movie['title']}' has vote count {movie['vote_count']} < {min_v}"
            )

    def test_functional_wrappers(self):
        """Test the top-level functional API wrappers."""
        recs_pop = get_popular_movies(top_n=3)
        self.assertEqual(len(recs_pop), 3)

        recs_top = get_top_movies(top_n=3, min_votes=100)
        self.assertEqual(len(recs_top), 3)
        self.assertGreaterEqual(recs_top[0]["vote_count"], 100)

        recs_genre = get_popular_by_genre(genre="Adventure", top_n=3)
        self.assertEqual(len(recs_genre), 3)
        self.assertIn("Adventure", recs_genre[0]["genres_list"])

if __name__ == "__main__":
    unittest.main()
