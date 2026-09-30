"""
Collaborative Filtering Model Training Script
Constructs normalized item-user matrix, computes item-item cosine similarity,
extracts top-K neighbor graph, and exports production-ready artifacts.
"""

import os
import pickle
import json
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

def train_recommender(
    data_dir: str = "data",
    output_model_dirs: list = ["ml/models", "backend/models"],
    top_k_neighbors: int = 100,
    min_similarity: float = 0.02
):
    print("=" * 60)
    print("STARTING RECOMMENDER MODEL TRAINING")
    print("=" * 60)

    # 1. Load data
    movies_path = os.path.join(data_dir, "processed", "movies_metadata.csv")
    ratings_path = os.path.join(data_dir, "processed", "interactions_clean.csv")

    if not os.path.exists(movies_path):
        from ml.preprocessing.preprocess import run_pipeline
        run_pipeline(data_dir=data_dir, output_dir=os.path.join(data_dir, "processed"))

    movies_df = pd.read_csv(movies_path)
    ratings_df = pd.read_csv(ratings_path)

    print(f"Loaded {len(movies_df)} movies and {len(ratings_df)} ratings.")

    # 2. Build index mappings
    unique_users = sorted(ratings_df['userId'].unique().tolist())
    unique_movies = sorted(movies_df['movieId'].unique().tolist())

    user_to_idx = {uid: i for i, uid in enumerate(unique_users)}
    idx_to_user = {i: uid for uid, i in user_to_idx.items()}

    movie_to_idx = {mid: i for i, mid in enumerate(unique_movies)}
    idx_to_movie = {i: mid for mid, i in movie_to_idx.items()}

    print(f"Mapped {len(unique_users)} users and {len(unique_movies)} movies.")

    # 3. User-mean centering for rating normalization
    user_means = ratings_df.groupby('userId')['rating'].mean().to_dict()
    ratings_df['centered_rating'] = ratings_df['rating'] - ratings_df['userId'].map(user_means)

    # 4. Construct sparse item-user matrix (rows = movies, cols = users)
    # Filter ratings for movies present in movies_df
    valid_ratings = ratings_df[ratings_df['movieId'].isin(movie_to_idx)].copy()
    
    rows = valid_ratings['movieId'].map(movie_to_idx).values
    cols = valid_ratings['userId'].map(user_to_idx).values
    vals = valid_ratings['centered_rating'].values

    n_movies = len(unique_movies)
    n_users = len(unique_users)

    item_user_sparse = csr_matrix((vals, (rows, cols)), shape=(n_movies, n_users), dtype=np.float32)
    print(f"Constructed sparse Item-User matrix: shape {item_user_sparse.shape} with {len(vals)} non-zero entries.")

    # 5. Compute Item-Item Cosine Similarity
    print("Computing item-item cosine similarity matrix...")
    item_sim = cosine_similarity(item_user_sparse, dense_output=False)
    print(f"Cosine similarity computed. Matrix non-zero elements: {item_sim.nnz}")

    # 6. Build Top-K Neighbors Dictionary for Sub-Millisecond Inference
    print(f"Extracting top-{top_k_neighbors} most similar neighbors for each movie...")
    item_neighbors = {}
    
    for m_idx in range(n_movies):
        mid = idx_to_movie[m_idx]
        sim_row = item_sim[m_idx].toarray().flatten()
        
        # Zero out self-similarity
        sim_row[m_idx] = 0.0

        # Filter strictly positive similarity above threshold
        cand_indices = np.where(sim_row >= min_similarity)[0]
        if len(cand_indices) == 0:
            item_neighbors[mid] = []
            continue

        cand_sims = sim_row[cand_indices]
        # Sort descending
        top_order = np.argsort(cand_sims)[::-1][:top_k_neighbors]
        
        neighbors = []
        for idx in top_order:
            cand_idx = cand_indices[idx]
            cand_mid = idx_to_movie[cand_idx]
            neighbors.append((int(cand_mid), float(round(cand_sims[idx], 4))))
        
        item_neighbors[mid] = neighbors

    # 7. Precompute Popularity and Genre mappings for Cold Start
    print("Pre-indexing genre popularity pools...")
    genre_popularity = {}
    all_genres = set()
    
    # Pre-parse genres
    for _, row in movies_df.iterrows():
        mid = int(row['movieId'])
        raw_genres = str(row['genres_joined']) if pd.notna(row['genres_joined']) else ""
        genres = [g.strip() for g in raw_genres.split('|') if g.strip()]
        for g in genres:
            all_genres.add(g)
            if g not in genre_popularity:
                genre_popularity[g] = []
            genre_popularity[g].append(mid)

    # Sort each genre by movie's popularity_score descending
    pop_scores_map = movies_df.set_index('movieId')['popularity_score'].to_dict()
    for g in genre_popularity:
        genre_popularity[g].sort(key=lambda m: pop_scores_map.get(m, 0.0), reverse=True)

    # Overall top popular movies
    popular_movies_ranked = movies_df.sort_values(by='popularity_score', ascending=False)['movieId'].tolist()

    # 8. Package Artifacts
    artifacts = {
        'item_neighbors': item_neighbors,
        'popular_movies_ranked': popular_movies_ranked,
        'genre_popularity': genre_popularity,
        'unique_movies': unique_movies,
        'unique_users': unique_users,
        'user_to_idx': user_to_idx,
        'idx_to_movie': idx_to_movie,
        'movie_to_idx': movie_to_idx,
        'top_k_neighbors': top_k_neighbors,
        'model_version': '1.0.0-item-cf'
    }

    # Save to all destination directories
    for m_dir in output_model_dirs:
        os.makedirs(m_dir, exist_ok=True)
        art_path = os.path.join(m_dir, "recommender_artifacts.pkl")
        with open(art_path, 'wb') as f:
            pickle.dump(artifacts, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Artifacts successfully saved to: '{art_path}'")

    print("=" * 60)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    return artifacts

if __name__ == "__main__":
    train_recommender()
