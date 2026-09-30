"""
Collaborative Filtering Model Training Pipeline
Uses Item-Item Cosine Similarity with User-Mean Centering on Sparse Matrices.
Generates production-ready serialized model artifacts and mappings.
"""

import os
import json
import pickle
import time
import numpy as np
import pandas as pd
from scipy.sparse import load_npz, csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

def train_collaborative_model(
    processed_dir: str = "data/processed",
    output_model_dirs: list = ["ml/models", "backend/models"],
    top_k_neighbors: int = 100,
    min_similarity: float = 0.02
) -> dict:
    """
    Train Item-Item Collaborative Filtering Model.
    
    Why Item-Item Collaborative Filtering?
    1. Superior Explainability: Recommendations can be directly explained by citing
       the specific movie the user previously rated ("Because you liked Inception").
    2. Real-Time Dynamic Serving: New user interactions can be instantly folded into
       recommendations without refactoring or retraining the full model.
    3. Computational Efficiency: Sparse matrix dot products allow fast neighbor graph
       construction and sub-millisecond online recommendation scoring.
    """
    print("=" * 80)
    print("       STARTING ITEM-ITEM COLLABORATIVE FILTERING MODEL TRAINING        ")
    print("=" * 80)
    start_time = time.time()

    # 1. Verify and Load Processed Data
    meta_path = os.path.join(processed_dir, "movies_metadata.csv")
    inter_path = os.path.join(processed_dir, "interactions_clean.csv")
    map_pkl_path = os.path.join(processed_dir, "id_mappings.pkl")
    item_user_path = os.path.join(processed_dir, "item_user_centered.npz")

    if not (os.path.exists(meta_path) and os.path.exists(inter_path) and os.path.exists(map_pkl_path)):
        print("Processed data missing. Running preprocessing pipeline...")
        from ml.preprocessing.preprocess import run_pipeline
        run_pipeline(data_dir="data", output_dir=processed_dir)

    print("[1/5] Loading processed datasets and ID mappings...")
    movies_df = pd.read_csv(meta_path)
    interactions_df = pd.read_csv(inter_path)
    with open(map_pkl_path, "rb") as f:
        mappings = pickle.load(f)

    user_to_idx = mappings["user_to_idx"]
    idx_to_user = mappings["idx_to_user"]
    movie_to_idx = mappings["movie_to_idx"]
    idx_to_movie = mappings["idx_to_movie"]
    n_users = mappings["n_users"]
    n_movies = mappings["n_movies"]

    print(f"      Users: {n_users:,} | Movies: {n_movies:,} | Interactions: {len(interactions_df):,}")

    # 2. Load or Reconstruct Item-User Centered Sparse Matrix
    print("[2/5] Loading sparse Item-User matrix (shape: n_movies x n_users)...")
    if os.path.exists(item_user_path):
        item_user_centered = load_npz(item_user_path)
    else:
        # Construct from interactions_df
        rows = interactions_df['movie_idx'].values
        cols = interactions_df['user_idx'].values
        vals = interactions_df['centered_rating'].values.astype(np.float32)
        item_user_centered = csr_matrix((vals, (rows, cols)), shape=(n_movies, n_users), dtype=np.float32)

    print(f"      Matrix shape: {item_user_centered.shape} with {item_user_centered.nnz:,} non-zero values.")

    # 3. Compute Item-Item Cosine Similarity Matrix
    print("[3/5] Computing Item-Item Cosine Similarity matrix...")
    sim_start = time.time()
    # item_user_centered has shape (n_movies, n_users)
    # Cosine similarity computes pairwise dot products normalized by L2 norms
    item_similarity_matrix = cosine_similarity(item_user_centered, dense_output=False)
    sim_elapsed = time.time() - sim_start
    print(f"      Similarity matrix computed in {sim_elapsed:.2f}s.")
    print(f"      Non-zero similarity entries: {item_similarity_matrix.nnz:,}")

    # 4. Prune to Top-K Nearest Neighbors per Movie
    print(f"[4/5] Extracting Top-{top_k_neighbors} nearest neighbors per movie (min_sim >= {min_similarity})...")
    item_neighbors = {}
    total_edges = 0

    for m_idx in range(n_movies):
        mid = idx_to_movie[m_idx]
        sim_row = item_similarity_matrix[m_idx].toarray().flatten()

        # Zero out self-similarity
        sim_row[m_idx] = 0.0

        # Filter positive similarities above threshold
        candidate_indices = np.where(sim_row >= min_similarity)[0]
        if len(candidate_indices) == 0:
            item_neighbors[mid] = []
            continue

        cand_sims = sim_row[candidate_indices]
        # Sort descending
        top_order = np.argsort(cand_sims)[::-1][:top_k_neighbors]

        neighbors_list = []
        for rank_idx in top_order:
            cand_idx = candidate_indices[rank_idx]
            cand_mid = int(idx_to_movie[cand_idx])
            sim_val = float(round(cand_sims[rank_idx], 4))
            neighbors_list.append((cand_mid, sim_val))

        item_neighbors[mid] = neighbors_list
        total_edges += len(neighbors_list)

    avg_neighbors = total_edges / n_movies if n_movies > 0 else 0
    print(f"      Neighbor graph built: {total_edges:,} directed edges (average {avg_neighbors:.1f} neighbors per movie).")

    # 5. Build Training User History Lookup Cache
    print("[5/5] Building user rating history cache for training users...")
    train_user_history = {}
    for uid, group in interactions_df.groupby('userId'):
        # Store tuple of (movieId, rating)
        train_user_history[int(uid)] = list(zip(group['movieId'].astype(int), group['rating'].astype(float)))

    # Package Artifacts
    training_time = time.time() - start_time
    model_artifacts = {
        "model_type": "item_item_collaborative_filtering",
        "algorithm": "normalized_cosine_similarity_top_k",
        "version": "2.0.0",
        "trained_at": pd.Timestamp.now().isoformat(),
        "training_time_seconds": round(training_time, 2),
        "parameters": {
            "top_k_neighbors": top_k_neighbors,
            "min_similarity": min_similarity,
            "n_users": n_users,
            "n_movies": n_movies,
            "total_interactions": len(interactions_df)
        },
        "item_neighbors": item_neighbors,
        "train_user_history": train_user_history,
        "user_to_idx": user_to_idx,
        "idx_to_user": idx_to_user,
        "movie_to_idx": movie_to_idx,
        "idx_to_movie": idx_to_movie
    }

    # Save to all destination directories
    for out_dir in output_model_dirs:
        os.makedirs(out_dir, exist_ok=True)
        art_path = os.path.join(out_dir, "collaborative_model.pkl")
        with open(art_path, "wb") as f:
            pickle.dump(model_artifacts, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        file_size_mb = os.path.getsize(art_path) / (1024 * 1024)
        print(f"      Saved model artifact: '{art_path}' ({file_size_mb:.2f} MB)")

    # Save lightweight JSON metadata summary
    summary_meta = {
        "model_type": model_artifacts["model_type"],
        "algorithm": model_artifacts["algorithm"],
        "version": model_artifacts["version"],
        "trained_at": model_artifacts["trained_at"],
        "training_time_seconds": model_artifacts["training_time_seconds"],
        "parameters": model_artifacts["parameters"],
        "graph_statistics": {
            "total_movies": n_movies,
            "total_edges": total_edges,
            "average_neighbors_per_movie": round(avg_neighbors, 2)
        }
    }
    meta_json_path = os.path.join(output_model_dirs[0], "collaborative_model_meta.json")
    with open(meta_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_meta, f, indent=2)
    print(f"      Saved model summary JSON: '{meta_json_path}'")

    print("=" * 80)
    print(f"   TRAINING COMPLETED SUCCESSFULLY IN {training_time:.2f} SECONDS!    ")
    print("=" * 80)
    return model_artifacts

if __name__ == "__main__":
    train_collaborative_model()
