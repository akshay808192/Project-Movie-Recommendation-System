"""
Unit and Integration Tests for FastAPI REST API Endpoints
Covers:
- GET /api/movies/popular
- GET /api/movies/search
- GET /api/movies/{movie_id}
- GET /api/recommendations (Cold-start popularity for new user)
- GET /api/recommendations/{user_id} (Hybrid recommendation engine)
- POST /api/users/register
- POST /api/users/login
- POST /api/interactions/rating
- POST /api/interactions/like
- POST /api/interactions/watch
- GET /api/users/{user_id}/history
"""

import time
import unittest
from fastapi.testclient import TestClient
from backend.app.main import app


class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.timestamp = int(time.time() * 1000)
        cls.test_username = f"endpoint_user_{cls.timestamp}"
        cls.test_email = f"endpoint_{cls.timestamp}@test.com"
        cls.test_password = "password123"

    def test_01_health_check(self):
        """Test health endpoint."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "healthy")

    def test_02_popular_movies(self):
        """Test GET /api/movies/popular."""
        res = self.client.get("/api/movies/popular?limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("movies", data)
        self.assertGreaterEqual(len(data["movies"]), 1)
        self.assertIn("popularity_score", data["movies"][0])

    def test_03_search_movies(self):
        """Test GET /api/movies/search."""
        res = self.client.get("/api/movies/search?query=godfather&limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data["movies"]), 1)
        self.assertTrue(any("godfather" in m["title"].lower() for m in data["movies"]))

    def test_04_movie_details_and_not_found(self):
        """Test GET /api/movies/{movie_id} and 404 for invalid ID."""
        # Valid ID
        res = self.client.get("/api/movies/858")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["movieId"], 858)
        self.assertIn("Godfather", data["title"])
        self.assertIn("similar_movies", data)

        # Non-existent ID
        res_404 = self.client.get("/api/movies/99999999")
        self.assertEqual(res_404.status_code, 404)

    def test_05_cold_start_recommendations(self):
        """Test GET /api/recommendations returns popularity recommendations for new users."""
        res = self.client.get("/api/recommendations?limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["strategy"], "popularity")
        self.assertEqual(data["user_interaction_count"], 0)
        self.assertEqual(len(data["recommendations"]), 5)
        for rec in data["recommendations"]:
            self.assertIn("movieId", rec)
            self.assertIn("title", rec)
            self.assertIn("explanation", rec)

    def test_06_user_registration_and_login(self):
        """Test POST /api/users/register and POST /api/users/login."""
        # 1. Register
        reg_res = self.client.post("/api/users/register", json={
            "username": self.test_username,
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(reg_res.status_code, 201)
        reg_data = reg_res.json()
        self.assertIn("access_token", reg_data)
        user_id = reg_data["user"]["id"]
        token = reg_data["access_token"]

        # 2. Duplicate registration (should return 400)
        dup_res = self.client.post("/api/users/register", json={
            "username": self.test_username,
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(dup_res.status_code, 400)

        # 3. Successful login
        login_res = self.client.post("/api/users/login", json={
            "username": self.test_username,
            "password": self.test_password
        })
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.json()
        self.assertIn("access_token", login_data)

        # 4. Failed login (wrong password -> 401)
        fail_res = self.client.post("/api/users/login", json={
            "username": self.test_username,
            "password": "wrong_password_here"
        })
        self.assertEqual(fail_res.status_code, 401)

        TestAPIEndpoints.user_id = user_id
        TestAPIEndpoints.token = token

    def test_07_interactions_rating(self):
        """Test POST /api/interactions/rating and validation."""
        headers = {"Authorization": f"Bearer {self.token}"}

        # Valid rating
        rate_res = self.client.post(
            "/api/interactions/rating",
            json={"user_id": self.user_id, "movie_id": 260, "rating": 5.0},
            headers=headers
        )
        self.assertEqual(rate_res.status_code, 200)
        rate_data = rate_res.json()
        self.assertEqual(rate_data["rating"], 5.0)
        self.assertIn("Star Wars", rate_data["title"])

        # Invalid rating out of bounds (> 5.0 -> 422)
        inv_res = self.client.post(
            "/api/interactions/rating",
            json={"user_id": self.user_id, "movie_id": 260, "rating": 7.5},
            headers=headers
        )
        self.assertEqual(inv_res.status_code, 422)

    def test_08_interactions_like(self):
        """Test POST /api/interactions/like."""
        headers = {"Authorization": f"Bearer {self.token}"}
        res = self.client.post(
            "/api/interactions/like",
            json={"user_id": self.user_id, "movie_id": 1196},
            headers=headers
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["is_liked"])

    def test_09_interactions_watch(self):
        """Test POST /api/interactions/watch."""
        headers = {"Authorization": f"Bearer {self.token}"}
        res = self.client.post(
            "/api/interactions/watch",
            json={"user_id": self.user_id, "movie_id": 2571},
            headers=headers
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["movie_id"], 2571)
        self.assertIn("Matrix", data["title"])

    def test_10_user_history(self):
        """Test GET /api/users/{user_id}/history."""
        res = self.client.get(f"/api/users/{self.user_id}/history")
        self.assertEqual(res.status_code, 200)
        history = res.json()
        self.assertGreaterEqual(len(history), 1)

    def test_11_recommendations_by_user_id_hybrid_progression(self):
        """Test GET /api/recommendations/{user_id} transitions across hybrid stages."""
        headers = {"Authorization": f"Bearer {self.token}"}

        # User currently has 1 rating (from test_07) -> should route to hybrid
        res_hybrid = self.client.get(f"/api/recommendations/{self.user_id}?limit=5")
        self.assertEqual(res_hybrid.status_code, 200)
        hybrid_data = res_hybrid.json()
        self.assertEqual(hybrid_data["strategy"], "hybrid")

        # Now add ratings to bring user to >= 5 interactions
        seed_mids = [1196, 2571, 589, 1210]
        for mid in seed_mids:
            self.client.post(
                "/api/interactions/rating",
                json={"user_id": self.user_id, "movie_id": mid, "rating": 5.0},
                headers=headers
            )

        # User now has 5 ratings -> should route to collaborative
        res_cf = self.client.get(f"/api/recommendations/{self.user_id}?limit=5")
        self.assertEqual(res_cf.status_code, 200)
        cf_data = res_cf.json()
        self.assertEqual(cf_data["strategy"], "collaborative")
        self.assertGreaterEqual(len(cf_data["recommendations"]), 1)


if __name__ == "__main__":
    unittest.main()
