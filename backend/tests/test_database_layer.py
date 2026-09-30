"""
Database Layer & Workflow Integration Test
Tests the complete 7-step user interaction lifecycle:
1. Register user
2. Login
3. Rate movie
4. Like movie
5. Add movie to history
6. Retrieve user history
7. Retrieve recommendations
"""

import time
import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.connection import get_db_connection
from backend.app.database import crud


class TestDatabaseLayerWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.conn = get_db_connection()
        cls.cursor = cls.conn.cursor()

        cls.ts = int(time.time() * 1000)
        cls.username = f"db_user_{cls.ts}"
        cls.email = f"db_user_{cls.ts}@example.com"
        cls.password = "SecurePassword123!"

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_01_movies_table_seeded(self):
        """Verify the movies table is seeded with actual movie IDs from MovieLens."""
        self.cursor.execute("SELECT COUNT(*) FROM movies;")
        count = self.cursor.fetchone()[0]
        self.assertGreaterEqual(count, 9000, "Movies table should contain at least 9,000 movies from dataset.")

        # Check specific known MovieLens IDs
        known_mids = [1, 260, 318, 858, 2571]
        for mid in known_mids:
            self.cursor.execute("SELECT movie_id, title FROM movies WHERE movie_id = ?;", (mid,))
            row = self.cursor.fetchone()
            self.assertIsNotNone(row, f"Movie with dataset ID {mid} should exist in SQLite.")
            self.assertEqual(row['movie_id'], mid)

    def test_02_register_user(self):
        """Step 1: Register user."""
        res = self.client.post("/api/users/register", json={
            "username": self.username,
            "email": self.email,
            "password": self.password
        })
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["username"], self.username)

        TestDatabaseLayerWorkflow.user_id = data["user"]["id"]
        TestDatabaseLayerWorkflow.token = data["access_token"]

        # Verify user is saved in SQLite database
        self.cursor.execute("SELECT id, username, email FROM users WHERE id = ?;", (self.user_id,))
        user_row = self.cursor.fetchone()
        self.assertIsNotNone(user_row)
        self.assertEqual(user_row['username'], self.username)

    def test_03_login_user(self):
        """Step 2: Login user."""
        res = self.client.post("/api/users/login", json={
            "username": self.username,
            "password": self.password
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["id"], self.user_id)

    def test_04_rate_movie(self):
        """Step 3: Rate a movie and verify database storage."""
        headers = {"Authorization": f"Bearer {self.token}"}
        movie_to_rate = 260  # Star Wars: Episode IV
        rating_val = 5.0

        res = self.client.post("/api/interactions/rating", json={
            "user_id": self.user_id,
            "movie_id": movie_to_rate,
            "rating": rating_val
        }, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["movie_id"], movie_to_rate)
        self.assertEqual(data["rating"], rating_val)

        # Direct database verification
        self.cursor.execute("SELECT rating FROM ratings WHERE user_id = ? AND movie_id = ?;", (self.user_id, movie_to_rate))
        r_row = self.cursor.fetchone()
        self.assertIsNotNone(r_row, "Rating must be stored in ratings table.")
        self.assertEqual(float(r_row['rating']), rating_val)

        # Backwards-compatible table check
        self.cursor.execute("SELECT rating FROM user_ratings WHERE user_id = ? AND movie_id = ?;", (self.user_id, movie_to_rate))
        ur_row = self.cursor.fetchone()
        self.assertIsNotNone(ur_row, "Rating must be stored in user_ratings table.")

    def test_05_like_movie(self):
        """Step 4: Like a movie and verify database storage."""
        headers = {"Authorization": f"Bearer {self.token}"}
        movie_to_like = 858  # The Godfather

        res = self.client.post("/api/interactions/like", json={
            "user_id": self.user_id,
            "movie_id": movie_to_like
        }, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["is_liked"])

        # Direct database verification
        self.cursor.execute("SELECT id FROM likes WHERE user_id = ? AND movie_id = ?;", (self.user_id, movie_to_like))
        l_row = self.cursor.fetchone()
        self.assertIsNotNone(l_row, "Like must be stored in likes table.")

        # Backwards-compatible table check
        self.cursor.execute("SELECT id FROM user_favorites WHERE user_id = ? AND movie_id = ?;", (self.user_id, movie_to_like))
        uf_row = self.cursor.fetchone()
        self.assertIsNotNone(uf_row, "Like must be stored in user_favorites table.")

    def test_06_add_movie_to_history(self):
        """Step 5: Add movie to history and verify database storage."""
        headers = {"Authorization": f"Bearer {self.token}"}
        movie_watched = 2571  # The Matrix

        res = self.client.post("/api/interactions/watch", json={
            "user_id": self.user_id,
            "movie_id": movie_watched
        }, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["movie_id"], movie_watched)

        # Direct database verification
        self.cursor.execute("SELECT id FROM watch_history WHERE user_id = ? AND movie_id = ?;", (self.user_id, movie_watched))
        wh_row = self.cursor.fetchone()
        self.assertIsNotNone(wh_row, "Watch event must be stored in watch_history table.")

    def test_07_retrieve_user_history(self):
        """Step 6: Retrieve user history."""
        res = self.client.get(f"/api/users/{self.user_id}/history")
        self.assertEqual(res.status_code, 200)
        history = res.json()
        self.assertGreaterEqual(len(history), 1)
        history_movie_ids = [h["movie_id"] for h in history]
        # Movie watched in step 5 (2571) and movie rated in step 3 (260) should both appear
        self.assertIn(2571, history_movie_ids)
        self.assertIn(260, history_movie_ids)

    def test_08_retrieve_recommendations(self):
        """Step 7: Retrieve recommendations for user, verifying exclusions and strategy."""
        res = self.client.get(f"/api/recommendations/{self.user_id}?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("strategy", data)
        self.assertIn("recommendations", data)
        self.assertGreaterEqual(len(data["recommendations"]), 1)

        rec_mids = [r["movieId"] for r in data["recommendations"]]
        # Already interacted movies must NOT be recommended
        self.assertNotIn(260, rec_mids, "Rated movie (260) must be excluded from recommendations.")
        self.assertNotIn(858, rec_mids, "Liked movie (858) must be excluded from recommendations.")
        self.assertNotIn(2571, rec_mids, "Watched movie (2571) must be excluded from recommendations.")


if __name__ == "__main__":
    unittest.main()
