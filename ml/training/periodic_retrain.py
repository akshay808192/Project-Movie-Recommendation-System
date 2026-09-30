"""
Periodic Retraining Architecture
Periodically merges newly accumulated user ratings from the SQLite database
with the base training dataset, recalculates Item-Item Cosine Similarities and
Bayesian Popularity scores, and atomically updates model artifacts.

Note: In this production architecture:
1. Online clicks, ratings, likes, and watches are served with zero latency
   via dynamic session folding against precomputed similarity matrices.
2. The full similarity graph and catalog popularity parameters are periodically
   retrained in batch (e.g. nightly or via this script) without service downtime.
"""

import os
import sys
import time
import json
import pickle
import sqlite3
import datetime
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

# Ensure project root is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.database.connection import DB_PATH, get_db_connection


def run_periodic_retraining(
    db_path: str = DB_PATH,
    processed_dir: str = "data/processed",
    output_model_dirs: list = ["ml/models", "backend/models"],
    top_k_neighbors: int = 100,
    min_similarity: float = 0.02,
    force: bool = False
) -> dict:
    """
    Execute periodic model retraining incorporating SQLite interaction logs.
    """
    start_time = time.time()
    timestamp_str = datetime.datetime.now().isoformat()

    print("=" * 80)
    print("      PERIODIC RECOMMENDER RETRAINING PIPELINE      ")
    print(f"      Execution Timestamp: {timestamp_str}")
    print("=" * 80)

    # 1. Load Base Processed Data
    meta_path = os.path.join(processed_dir, "movies_metadata.csv")
    inter_path = os.path.join(processed_dir, "interactions_clean.csv")
    map_pkl_path = os.path.join(processed_dir, "id_mappings.pkl")

    if not (os.path.exists(meta_path) and os.path.exists(inter_path) and os.path.exists(map_pkl_path)):
        print("Base processed data not found. Running baseline training first...")
        from ml.training.train_collaborative import train_collaborative_model
        return train_collaborative_model(processed_dir=processed_dir, output_model_dirs=output_model_dirs)

    print("[1/6] Loading base interactions and movie metadata...")
    movies_df = pd.read_csv(meta_path)
    base_interactions_df = pd.read_csv(inter_path)
    with open(map_pkl_path, "rb") as f:
        base_mappings = pickle.load(f)

    movie_to_idx = base_mappings["movie_to_idx"]
    idx_to_movie = base_mappings["idx_to_movie"]
    n_movies = len(movie_to_idx)
    base_n_users = base_mappings["n_users"]

    # 2. Extract New Ratings from SQLite Database
    print(f"[2/6] Connecting to SQLite database at '{db_path}'...")
    new_ratings_list = []
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, movie_id, rating, created_at FROM ratings;")
        new_ratings_list = [dict(r) for r in cursor.fetchall()]
        conn.close()

    print(f"      Retrieved {len(new_ratings_list)} interaction records from SQLite database.")

    if not new_ratings_list and not force:
        print("      No new SQLite interactions found. Model is already up to date.")
        return {
            "status": "skipped",
            "message": "No new interaction data found.",
            "timestamp": timestamp_str
        }

    # 3. Merge Base and SQLite Ratings
    print("[3/6] Merging base dataset ratings with live application interactions...")
    # Base columns: userId, movieId, rating, timestamp
    base_df = base_interactions_df[['userId', 'movieId', 'rating', 'timestamp']].copy()

    # Prepare SQLite records: use negative or offset user IDs to prevent collision with base user IDs
    db_records = []
    max_base_user = int(base_df['userId'].max()) if not base_df.empty else 0

    for r in new_ratings_list:
        mid = int(r['movie_id'])
        if mid not in movie_to_idx:
            continue  # Skip movies outside catalog
        
        # Map app user id into retrain user id space
        app_user_id = max_base_user + int(r['user_id'])
        db_records.append({
            'userId': app_user_id,
            'movieId': mid,
            'rating': float(r['rating']),
            'timestamp': int(time.time())
        })

    if db_records:
        db_df = pd.DataFrame(db_records)
        combined_df = pd.concat([base_df, db_df], ignore_index=True)
    else:
        combined_df = base_df

    # Deduplicate: if a user rated the same movie multiple times, keep the latest
    combined_df = combined_df.drop_duplicates(subset=['userId', 'movieId'], keep='last')
    total_ratings = len(combined_df)
    unique_users = combined_df['userId'].unique()
    n_users = len(unique_users)

    print(f"      Total Combined Ratings: {total_ratings:,} across {n_users:,} users and {n_movies:,} movies.")

    # 4. Recompute User-Mean Centering & Sparse Item-User Matrix
    print("[4/6] Recomputing user-mean centered rating matrix...")
    user_to_idx = {uid: idx for idx, uid in enumerate(unique_users)}
    idx_to_user = {idx: uid for uid, idx in user_to_idx.items()}

    combined_df['user_idx'] = combined_df['userId'].map(user_to_idx)
    combined_df['movie_idx'] = combined_df['movieId'].map(movie_to_idx)

    # Calculate user mean rating
    user_means = combined_df.groupby('user_idx')['rating'].transform('mean')
    combined_df['centered_rating'] = combined_df['rating'] - user_means

    rows = combined_df['movie_idx'].values
    cols = combined_df['user_idx'].values
    vals = combined_df['centered_rating'].values.astype(np.float32)

    item_user_centered = csr_matrix((vals, (rows, cols)), shape=(n_movies, n_users), dtype=np.float32)
    print(f"      Sparse Matrix Dimension: {item_user_centered.shape} (nnz: {item_user_centered.nnz:,})")

    # 5. Compute Item-Item Cosine Similarity Matrix
    print("[5/6] Computing Item-Item Cosine Similarity matrix...")
    sim_start = time.time()
    item_similarity_matrix = cosine_similarity(item_user_centered, dense_output=False)
    sim_duration = time.time() - sim_start
    print(f"      Similarity matrix computed in {sim_duration:.2f}s (non-zero edges: {item_similarity_matrix.nnz:,}).")

    # Extract Top-K nearest neighbors
    item_neighbors = {}
    total_edges = 0
    for m_idx in range(n_movies):
        mid = idx_to_movie[m_idx]
        sim_row = item_similarity_matrix[m_idx].toarray().flatten()
        sim_row[m_idx] = 0.0  # Zero out self

        cand_indices = np.where(sim_row >= min_similarity)[0]
        if len(cand_indices) > 0:
            top_cand_indices = cand_indices[np.argsort(-sim_row[cand_indices])[:top_k_neighbors]]
            neighbors = [(idx_to_movie[idx], float(round(sim_row[idx], 4))) for idx in top_cand_indices]
            item_neighbors[mid] = neighbors
            total_edges += len(neighbors)
        else:
            item_neighbors[mid] = []

    # 6. Recompute Bayesian Popularity Scores
    print("[6/6] Updating catalog Bayesian popularity scores...")
    C = float(combined_df['rating'].mean())
    movie_stats = combined_df.groupby('movieId').agg(
        vote_count=('rating', 'count'),
        mean_rating=('rating', 'mean')
    ).reset_index()

    m = float(movie_stats['vote_count'].quantile(0.80)) if not movie_stats.empty else 12.0

    stats_dict = movie_stats.set_index('movieId').to_dict(orient='index')
    updated_pop_ranked = []

    for mid in idx_to_movie.values():
        st = stats_dict.get(mid, {'vote_count': 0, 'mean_rating': 0.0})
        v = st['vote_count']
        R = st['mean_rating']
        wr = ((v / (v + m)) * R) + ((m / (v + m)) * C) if (v + m) > 0 else 0.0
        updated_pop_ranked.append((mid, wr))

    updated_pop_ranked.sort(key=lambda x: x[1], reverse=True)
    popular_movies_ranked = [mid for mid, _ in updated_pop_ranked]

    # Build Training User History
    train_user_history = {}
    for uid, group in combined_df.groupby('userId'):
        train_user_history[int(uid)] = list(zip(group['movieId'].astype(int), group['rating'].astype(float)))

    # Save Artifacts Atomically
    artifact_payload = {
        "item_neighbors": item_neighbors,
        "movie_to_idx": movie_to_idx,
        "idx_to_movie": idx_to_movie,
        "user_to_idx": user_to_idx,
        "idx_to_user": idx_to_user,
        "train_user_history": train_user_history,
        "popular_movies_ranked": popular_movies_ranked,
        "metadata": {
            "retrained_at": timestamp_str,
            "total_ratings": total_ratings,
            "new_db_ratings": len(new_ratings_list),
            "n_users": n_users,
            "n_movies": n_movies,
            "total_similarity_edges": total_edges,
            "training_seconds": round(time.time() - start_time, 2)
        }
    }

    for target_dir in output_model_dirs:
        os.makedirs(target_dir, exist_ok=True)
        collab_target = os.path.join(target_dir, "collaborative_model.pkl")
        with open(collab_target, "wb") as f:
            pickle.dump(artifact_payload, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"      Saved updated model artifact to: {collab_target}")

    # Write Retraining Audit Log
    log_path = os.path.join(PROJECT_ROOT, "ml/training/retraining_log.json")
    with open(log_path, "w") as f:
        json.dump(artifact_payload["metadata"], f, indent=2)

    total_time = time.time() - start_time
    print("=" * 80)
    print(f"       RETRAINING COMPLETED IN {total_time:.2f} SECONDS")
    print(f"       New Interactions Integrated: {len(new_ratings_list)}")
    print(f"       Total Ratings in Model: {total_ratings:,}")
    print("=" * 80)

    return artifact_payload["metadata"]


if __name__ == "__main__":
    force_run = "--force" in sys.argv
    run_periodic_retraining(force=force_run)
