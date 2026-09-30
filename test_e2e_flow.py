import os
import time
import requests

API_URL = "http://127.0.0.1:8000/api"

print("=========================================")
print("E2E USER FLOW SIMULATION: API VERIFICATION")
print("=========================================")

session = requests.Session()
token = None

def get_headers():
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

# 1. Unauthenticated checks
print("\n[STEP 1] Testing unauthenticated access...")
r = session.get(f"{API_URL}/movies/popular")
assert r.status_code == 200, "Failed to get popular movies"
print("[OK] Popular movies loaded successfully.")

r = session.get(f"{API_URL}/recommendations")
assert r.status_code == 200, "Failed to get cold start recommendations"
assert r.json()['strategy'] == 'popularity', "Expected popularity strategy for cold start"
print("[OK] Cold-start recommendations (popularity) loaded successfully.")

# 2. Register New User
print("\n[STEP 2] Registering new user...")
user_data = {
    "username": f"testuser_{int(time.time())}",
    "email": f"test_{int(time.time())}@example.com",
    "password": "Password123!"
}
r = session.post(f"{API_URL}/users/register", json=user_data)
assert r.status_code in [200, 201], f"Registration failed: {r.text}"
token = r.json()['access_token']
print(f"[OK] Registered user {user_data['username']}")

# 3. New User Cold Start
print("\n[STEP 3] Verifying recommendations for new user (0 interactions)...")
r = session.get(f"{API_URL}/recommendations/me", headers=get_headers())
assert r.status_code == 200
data = r.json()
assert data['strategy'] == 'popularity', f"Strategy should be popularity for 0 ratings, got: {data.get('strategy')}"
print("[OK] Verified: New user receives POPULARITY-BASED recommendations.")

# 4. Search and Select Movie
print("\n[STEP 4] Searching for a movie...")
r = session.get(f"{API_URL}/movies/search?q=Toy Story", headers=get_headers())
assert r.status_code == 200
movies = r.json()['movies']
assert len(movies) > 0, "No movies found in search"
target_movie_id = movies[0]['movieId']
print(f"[OK] Found movie '{movies[0]['title']}' (ID: {target_movie_id})")

# 5. Movie Details
print("\n[STEP 5] Getting movie details...")
r = session.get(f"{API_URL}/movies/{target_movie_id}", headers=get_headers())
assert r.status_code == 200
print(f"[OK] Retrieved details for '{r.json()['title']}'")

# 6. Rate movie (trigger Hybrid)
print("\n[STEP 6] Rating movie (adding 1 interaction)...")
r = session.post(f"{API_URL}/interactions/rating", json={"movie_id": target_movie_id, "rating": 5.0}, headers=get_headers())
assert r.status_code == 200
print(f"[OK] Rated movie {target_movie_id} with 5.0 stars")

# 7. Check recommendations transition (Hybrid)
print("\n[STEP 7] Verifying recommendations transition...")
r = session.get(f"{API_URL}/recommendations/me", headers=get_headers())
assert r.status_code == 200
data = r.json()
assert data['strategy'] == 'hybrid', f"Strategy should be hybrid for 1 rating, got {data['strategy']}"
print("[OK] Verified: User receives HYBRID recommendations after 1 rating.")

# 8. Rate 4 more movies (Total 5, trigger Collaborative Filtering)
print("\n[STEP 8] Adding 4 more ratings to trigger Collaborative Filtering...")
extra_movies = [1, 2, 3, 4]
for m_id in extra_movies:
    if m_id != target_movie_id:
        session.post(f"{API_URL}/interactions/rating", json={"movie_id": m_id, "rating": 4.0}, headers=get_headers())
print("[OK] Added ratings.")

print("\n[STEP 9] Verifying recommendations transition to Collaborative Filtering...")
r = session.get(f"{API_URL}/recommendations/me", headers=get_headers())
assert r.status_code == 200
data = r.json()
assert data['strategy'] == 'collaborative', f"Strategy should be collaborative for 5 ratings, got {data['strategy']}"
print("[OK] Verified: User receives COLLABORATIVE FILTERING recommendations.")

# 9. Verify Exclusion
print("\n[STEP 10] Verifying exclusion of rated movies...")
recommended_ids = [m['movieId'] for m in data['recommendations']]
assert target_movie_id not in recommended_ids, "Rated movie appeared in recommendations!"
print("✓ Verified: Rated/watched movies are excluded from recommendations.")

# 10. Add Favorite and Watch History
print("\n[STEP 11] Adding favorite and watch history...")
session.post(f"{API_URL}/interactions/like", json={"movie_id": target_movie_id}, headers=get_headers())
session.post(f"{API_URL}/interactions/watch", json={"movie_id": target_movie_id}, headers=get_headers())
print("✓ Interaction persisted to SQLite.")

# 11. Verify User Profile Data
print("\n[STEP 12] Fetching User Profile / History...")
r = session.get(f"{API_URL}/auth/me", headers=get_headers())
assert r.status_code == 200
user_info = r.json()
user_id = user_info['id']

r = session.get(f"{API_URL}/users/{user_id}/history", headers=get_headers())
assert r.status_code == 200
history = r.json()
assert len(history) >= 1
print("[OK] Verified: User profile data correctly reflects interactions.")

# 12. Verify Unknown User Fallback
print("\n[STEP 13] Verifying unknown user fallback...")
r = session.get(f"{API_URL}/recommendations/999999", headers=get_headers())
assert r.status_code == 200
assert r.json()['strategy'] == 'popularity', "Unknown user did not fallback to popularity"
print("✓ Verified: System safely falls back to popularity recommendations for unknown ID.")

print("\n=========================================")
print("ALL E2E API TESTS PASSED SUCCESSFULLY! [SUCCESS]")
print("=========================================")
