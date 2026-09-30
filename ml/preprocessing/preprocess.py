"""
Complete Preprocessing Pipeline for Movie Recommendation System
Processes MovieLens dataset according to verified dataset schema and rules.
Outputs clean metadata, normalized interactions, mapped sparse matrices, and mappings.
"""

import os
import re
import json
import pickle
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, save_npz

# ==============================================================================
# 1. LOAD DATA
# ==============================================================================
def load_data(data_dir: str = "data") -> dict:
    """
    Load raw MovieLens CSV files from data directory.
    Does not modify original files.
    """
    print(f"[1/6] Loading raw dataset from '{data_dir}'...")
    movies_path = os.path.join(data_dir, "movies.csv")
    ratings_path = os.path.join(data_dir, "ratings.csv")
    links_path = os.path.join(data_dir, "links.csv")
    tags_path = os.path.join(data_dir, "tags.csv")

    if not os.path.exists(movies_path) or not os.path.exists(ratings_path):
        raise FileNotFoundError(f"Required dataset files not found in '{data_dir}'")

    movies_df = pd.read_csv(movies_path)
    ratings_df = pd.read_csv(ratings_path)
    links_df = pd.read_csv(links_path) if os.path.exists(links_path) else pd.DataFrame()
    tags_df = pd.read_csv(tags_path) if os.path.exists(tags_path) else pd.DataFrame()

    print(f"      Loaded movies.csv:  {len(movies_df):,} rows")
    print(f"      Loaded ratings.csv: {len(ratings_df):,} rows")
    print(f"      Loaded links.csv:   {len(links_df):,} rows")
    print(f"      Loaded tags.csv:    {len(tags_df):,} rows")

    return {
        "movies": movies_df,
        "ratings": ratings_df,
        "links": links_df,
        "tags": tags_df
    }

# ==============================================================================
# 2. CLEAN DATA
# ==============================================================================
def extract_year(title: str):
    """Extract release year from title string e.g. 'Toy Story (1995)' -> 1995"""
    match = re.search(r'\((\d{4})\)', str(title))
    if match:
        year = int(match.group(1))
        # Sanity check year range for cinema history (1888 to present)
        if 1888 <= year <= 2030:
            return year
    return None

def extract_clean_title(title: str):
    """Strip trailing (YYYY) from title string for clean user interface display"""
    return re.sub(r'\s*\(\d{4}\)\s*$', '', str(title)).strip()

def clean_data(raw_data: dict) -> dict:
    """
    Clean, validate, and deduplicate movies, ratings, links, and tags.
    """
    print("[2/6] Cleaning and validating raw data...")
    movies_df = raw_data["movies"].copy()
    ratings_df = raw_data["ratings"].copy()
    links_df = raw_data["links"].copy()
    tags_df = raw_data["tags"].copy()

    # --- A. Clean Movies ---
    # Drop rows missing movieId or title
    movies_df.dropna(subset=['movieId', 'title'], inplace=True)
    movies_df['movieId'] = movies_df['movieId'].astype(np.int64)

    # Remove duplicate movie IDs (preserve first occurrence)
    movies_df.drop_duplicates(subset=['movieId'], keep='first', inplace=True)

    # Normalize titles and extract release years
    movies_df['clean_title'] = movies_df['title'].apply(extract_clean_title)
    movies_df['year'] = movies_df['title'].apply(extract_year)

    # Parse pipe-separated genres list
    def parse_genres(g_str):
        if pd.isna(g_str) or str(g_str).strip() == '(no genres listed)':
            return []
        return [g.strip() for g in str(g_str).split('|') if g.strip()]

    movies_df['genres_list'] = movies_df['genres'].apply(parse_genres)

    # --- B. Clean Ratings ---
    # Drop missing values
    ratings_df.dropna(subset=['userId', 'movieId', 'rating', 'timestamp'], inplace=True)
    ratings_df['userId'] = ratings_df['userId'].astype(np.int64)
    ratings_df['movieId'] = ratings_df['movieId'].astype(np.int64)
    ratings_df['rating'] = ratings_df['rating'].astype(np.float64)
    ratings_df['timestamp'] = ratings_df['timestamp'].astype(np.int64)

    # Validate rating scale bounds (MovieLens explicit ratings: 0.5 to 5.0)
    valid_ratings_mask = (ratings_df['rating'] >= 0.5) & (ratings_df['rating'] <= 5.0)
    ratings_df = ratings_df[valid_ratings_mask]

    # Validate foreign key integrity: ratings must reference an existing movieId in movies_df
    valid_movie_ids = set(movies_df['movieId'])
    ratings_df = ratings_df[ratings_df['movieId'].isin(valid_movie_ids)]

    # Deduplicate ratings: if a user rated the same movie multiple times, keep the latest rating
    ratings_df.sort_values(by=['userId', 'movieId', 'timestamp'], ascending=[True, True, True], inplace=True)
    ratings_df.drop_duplicates(subset=['userId', 'movieId'], keep='last', inplace=True)

    # --- C. Clean Links ---
    if not links_df.empty:
        links_df.dropna(subset=['movieId'], inplace=True)
        links_df['movieId'] = links_df['movieId'].astype(np.int64)
        links_df = links_df[links_df['movieId'].isin(valid_movie_ids)]
        links_df.drop_duplicates(subset=['movieId'], keep='first', inplace=True)

        # Format IMDb ID with 7-digit zero padding (e.g. 114709 -> tt0114709)
        def format_imdb(val):
            if pd.notna(val):
                return f"tt{int(val):07d}"
            return None

        links_df['imdb_id_str'] = links_df['imdbId'].apply(format_imdb)
        links_df['tmdb_id_int'] = links_df['tmdbId'].apply(lambda x: int(x) if pd.notna(x) else None)
    else:
        links_df = pd.DataFrame(columns=['movieId', 'imdb_id_str', 'tmdb_id_int'])

    # --- D. Clean Tags ---
    if not tags_df.empty:
        tags_df.dropna(subset=['movieId', 'tag'], inplace=True)
        tags_df['movieId'] = tags_df['movieId'].astype(np.int64)
        tags_df = tags_df[tags_df['movieId'].isin(valid_movie_ids)]
        # Normalize tag text
        tags_df['clean_tag'] = tags_df['tag'].astype(str).str.strip().str.lower()
        tags_df = tags_df[tags_df['clean_tag'] != '']
        tags_df.drop_duplicates(subset=['userId', 'movieId', 'clean_tag'], keep='first', inplace=True)
    else:
        tags_df = pd.DataFrame(columns=['movieId', 'clean_tag'])

    print(f"      Cleaned movies:  {len(movies_df):,} records")
    print(f"      Cleaned ratings: {len(ratings_df):,} records")
    print(f"      Cleaned links:   {len(links_df):,} records")
    print(f"      Cleaned tags:    {len(tags_df):,} records")

    return {
        "movies": movies_df,
        "ratings": ratings_df,
        "links": links_df,
        "tags": tags_df
    }

# ==============================================================================
# 3. PREPARE MOVIE METADATA & POPULARITY METRICS
# ==============================================================================
def prepare_movie_metadata(cleaned_data: dict) -> pd.DataFrame:
    """
    Construct rich movie metadata table joined with links, aggregated tags,
    and precomputed Bayesian Weighted Rating popularity scores for cold-start.
    """
    print("[3/6] Preparing consolidated movie metadata and cold-start popularity...")
    movies_df = cleaned_data["movies"].copy()
    ratings_df = cleaned_data["ratings"].copy()
    links_df = cleaned_data["links"].copy()
    tags_df = cleaned_data["tags"].copy()

    # 1. Join Links (IMDb & TMDb)
    if not links_df.empty:
        movies_df = movies_df.merge(
            links_df[['movieId', 'imdb_id_str', 'tmdb_id_int']],
            on='movieId',
            how='left'
        )
    else:
        movies_df['imdb_id_str'] = None
        movies_df['tmdb_id_int'] = None

    # 2. Aggregate semantic tags per movie
    if not tags_df.empty:
        tags_agg = tags_df.groupby('movieId')['clean_tag'].apply(
            lambda t: sorted(list(set(t)))
        ).reset_index().rename(columns={'clean_tag': 'tags_list'})
        movies_df = movies_df.merge(tags_agg, on='movieId', how='left')
        movies_df['tags_list'] = movies_df['tags_list'].apply(lambda x: x if isinstance(x, list) else [])
    else:
        movies_df['tags_list'] = [[] for _ in range(len(movies_df))]

    # 3. Aggregate rating statistics per movie
    rating_stats = ratings_df.groupby('movieId').agg(
        vote_count=('rating', 'count'),
        mean_rating=('rating', 'mean')
    ).reset_index()

    movies_df = movies_df.merge(rating_stats, on='movieId', how='left')
    movies_df['vote_count'] = movies_df['vote_count'].fillna(0).astype(int)
    movies_df['mean_rating'] = movies_df['mean_rating'].fillna(0.0).round(2)

    # 4. Compute Bayesian Weighted Rating (WR) for Cold-Start Popularity
    # Formula: WR = (v / (v + m)) * R + (m / (v + m)) * C
    # C = Global mean rating across all ratings
    # m = Minimum review threshold (80th percentile of rated movies)
    C = float(ratings_df['rating'].mean())
    rated_subset = movies_df[movies_df['vote_count'] > 0]
    m = float(rated_subset['vote_count'].quantile(0.80)) if not rated_subset.empty else 12.0

    print(f"      Global Rating Mean C = {C:.4f}")
    print(f"      Vote Count Threshold m (80th percentile) = {m:.1f} votes")

    def compute_weighted_rating(row):
        v = row['vote_count']
        R = row['mean_rating']
        if v == 0:
            return 0.0
        return (v / (v + m)) * R + (m / (v + m)) * C

    movies_df['popularity_score'] = movies_df.apply(compute_weighted_rating, axis=1).round(3)

    # Export convenience fields
    movies_df['genres_joined'] = movies_df['genres_list'].apply(lambda gl: '|'.join(gl))
    movies_df['tags_joined'] = movies_df['tags_list'].apply(lambda tl: '|'.join(tl[:15]))

    return movies_df

# ==============================================================================
# 4. PREPARE INTERACTIONS & ID NORMALIZATION
# ==============================================================================
def prepare_interactions(ratings_df: pd.DataFrame, movies_df: pd.DataFrame):
    """
    Normalize user and movie IDs to contiguous 0-indexed integers
    while strictly preserving bidirectional lookup dictionaries.
    Computes user-mean centering for normalization.
    """
    print("[4/6] Normalizing IDs and constructing interaction features...")
    # Determine unique users and movies sorted deterministically
    unique_users = sorted(ratings_df['userId'].unique().tolist())
    unique_movies = sorted(movies_df['movieId'].unique().tolist())

    # Build bidirectional mapping dictionaries
    user_to_idx = {uid: idx for idx, uid in enumerate(unique_users)}
    idx_to_user = {idx: uid for uid, idx in user_to_idx.items()}

    movie_to_idx = {mid: idx for idx, mid in enumerate(unique_movies)}
    idx_to_movie = {idx: mid for mid, idx in movie_to_idx.items()}

    # Copy interactions and map contiguous indices
    interactions_df = ratings_df.copy()
    interactions_df['user_idx'] = interactions_df['userId'].map(user_to_idx).astype(np.int32)
    interactions_df['movie_idx'] = interactions_df['movieId'].map(movie_to_idx).astype(np.int32)

    # User-mean centering for rating normalization: r_tilde = r_ui - bar(r)_u
    user_means = interactions_df.groupby('userId')['rating'].transform('mean')
    interactions_df['user_mean'] = user_means.round(4)
    interactions_df['centered_rating'] = (interactions_df['rating'] - interactions_df['user_mean']).round(4)

    mappings = {
        "user_to_idx": user_to_idx,
        "idx_to_user": idx_to_user,
        "movie_to_idx": movie_to_idx,
        "idx_to_movie": idx_to_movie,
        "n_users": len(unique_users),
        "n_movies": len(unique_movies)
    }

    print(f"      Mapped {len(unique_users):,} users to contiguous indices [0 .. {len(unique_users)-1}]")
    print(f"      Mapped {len(unique_movies):,} movies to contiguous indices [0 .. {len(unique_movies)-1}]")

    return interactions_df, mappings

# ==============================================================================
# 5. CREATE USER-ITEM INTERACTION MATRIX
# ==============================================================================
def create_user_item_matrix(interactions_df: pd.DataFrame, n_users: int, n_movies: int):
    """
    Construct sparse CSR user-item rating matrices.
    Returns:
    - user_item_raw: CSR matrix of raw ratings (shape: n_users x n_movies)
    - user_item_centered: CSR matrix of user-mean centered ratings
    - item_user_centered: Transposed CSR matrix (shape: n_movies x n_users) for Item-Item CF
    """
    print("[5/6] Building sparse interaction matrices...")
    rows = interactions_df['user_idx'].values
    cols = interactions_df['movie_idx'].values
    raw_vals = interactions_df['rating'].values.astype(np.float32)
    centered_vals = interactions_df['centered_rating'].values.astype(np.float32)

    user_item_raw = csr_matrix((raw_vals, (rows, cols)), shape=(n_users, n_movies), dtype=np.float32)
    user_item_centered = csr_matrix((centered_vals, (rows, cols)), shape=(n_users, n_movies), dtype=np.float32)
    item_user_centered = user_item_centered.T.tocsr()

    sparsity = (1.0 - (user_item_raw.nnz / (n_users * n_movies))) * 100

    print(f"      User-Item Matrix shape: {user_item_raw.shape}")
    print(f"      Non-zero entries (ratings): {user_item_raw.nnz:,}")
    print(f"      Matrix Sparsity: {sparsity:.2f}%")

    return {
        "user_item_raw": user_item_raw,
        "user_item_centered": user_item_centered,
        "item_user_centered": item_user_centered,
        "sparsity_pct": round(sparsity, 2)
    }

# ==============================================================================
# 6. SAVE PROCESSED DATA
# ==============================================================================
def save_processed_data(
    movies_metadata_df: pd.DataFrame,
    interactions_df: pd.DataFrame,
    mappings: dict,
    matrices: dict,
    output_dir: str = "data/processed"
):
    """
    Persist all processed datasets, sparse matrices, mappings, and metadata summary.
    """
    print(f"[6/6] Persisting processed data to '{output_dir}'...")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Save Movie Metadata CSV
    meta_path = os.path.join(output_dir, "movies_metadata.csv")
    movies_metadata_df.to_csv(meta_path, index=False)
    print(f"      Saved: {meta_path} ({len(movies_metadata_df):,} records)")

    # 2. Save Clean Interactions CSV
    inter_path = os.path.join(output_dir, "interactions_clean.csv")
    interactions_df.to_csv(inter_path, index=False)
    print(f"      Saved: {inter_path} ({len(interactions_df):,} records)")

    # 3. Save Mappings (JSON & Pickle)
    map_json_path = os.path.join(output_dir, "id_mappings.json")
    with open(map_json_path, 'w', encoding='utf-8') as f:
        # Convert integer keys to str for JSON compatibility
        json_mappings = {
            "n_users": mappings["n_users"],
            "n_movies": mappings["n_movies"],
            "user_to_idx": {str(k): v for k, v in mappings["user_to_idx"].items()},
            "idx_to_user": {str(k): v for k, v in mappings["idx_to_user"].items()},
            "movie_to_idx": {str(k): v for k, v in mappings["movie_to_idx"].items()},
            "idx_to_movie": {str(k): v for k, v in mappings["idx_to_movie"].items()},
        }
        json.dump(json_mappings, f, indent=2)
    print(f"      Saved: {map_json_path}")

    map_pkl_path = os.path.join(output_dir, "id_mappings.pkl")
    with open(map_pkl_path, 'wb') as f:
        pickle.dump(mappings, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"      Saved: {map_pkl_path}")

    # 4. Save Sparse Matrices
    raw_mat_path = os.path.join(output_dir, "user_item_raw.npz")
    save_npz(raw_mat_path, matrices["user_item_raw"])
    print(f"      Saved: {raw_mat_path}")

    centered_mat_path = os.path.join(output_dir, "user_item_centered.npz")
    save_npz(centered_mat_path, matrices["user_item_centered"])
    print(f"      Saved: {centered_mat_path}")

    item_user_path = os.path.join(output_dir, "item_user_centered.npz")
    save_npz(item_user_path, matrices["item_user_centered"])
    print(f"      Saved: {item_user_path}")

    # 5. Also copy movies_metadata.csv as movies_processed.csv in data/ for direct backend compatibility
    compat_path = os.path.join("data", "movies_processed.csv")
    movies_metadata_df.to_csv(compat_path, index=False)
    print(f"      Updated root compatibility file: {compat_path}")

    # 6. Save Preprocessing Summary Manifest
    summary_manifest = {
        "status": "success",
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_movies": len(movies_metadata_df),
        "total_users": mappings["n_users"],
        "total_interactions": len(interactions_df),
        "matrix_shape": [mappings["n_users"], mappings["n_movies"]],
        "sparsity_pct": matrices["sparsity_pct"],
        "min_rating": float(interactions_df['rating'].min()),
        "max_rating": float(interactions_df['rating'].max()),
        "mean_rating": float(round(interactions_df['rating'].mean(), 4)),
        "artifacts_generated": [
            "movies_metadata.csv",
            "interactions_clean.csv",
            "id_mappings.json",
            "id_mappings.pkl",
            "user_item_raw.npz",
            "user_item_centered.npz",
            "item_user_centered.npz"
        ]
    }
    summary_path = os.path.join(output_dir, "preprocessing_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_manifest, f, indent=2)
    print(f"      Saved: {summary_path}")

    return summary_manifest

# ==============================================================================
# MAIN PREPROCESSING PIPELINE ENTRY POINT
# ==============================================================================
def run_pipeline(data_dir: str = "data", output_dir: str = "data/processed"):
    print("=" * 80)
    print("          STARTING REPRODUCIBLE DATA PREPROCESSING PIPELINE             ")
    print("=" * 80)

    # 1. Load Data
    raw_data = load_data(data_dir=data_dir)

    # 2. Clean Data
    cleaned_data = clean_data(raw_data)

    # 3. Prepare Movie Metadata
    movies_metadata = prepare_movie_metadata(cleaned_data)

    # 4. Prepare Interactions & Contiguous Mappings
    interactions_clean, mappings = prepare_interactions(
        ratings_df=cleaned_data["ratings"],
        movies_df=movies_metadata
    )

    # 5. Create Interaction Matrices
    matrices = create_user_item_matrix(
        interactions_df=interactions_clean,
        n_users=mappings["n_users"],
        n_movies=mappings["n_movies"]
    )

    # 6. Save Processed Artifacts
    manifest = save_processed_data(
        movies_metadata_df=movies_metadata,
        interactions_df=interactions_clean,
        mappings=mappings,
        matrices=matrices,
        output_dir=output_dir
    )

    print("=" * 80)
    print("          PREPROCESSING PIPELINE COMPLETED SUCCESSFULLY!                ")
    print(f"          Processed Catalog: {manifest['total_movies']:,} movies")
    print(f"          Clean Interactions: {manifest['total_interactions']:,} ratings")
    print(f"          Matrix Sparsity: {manifest['sparsity_pct']}%")
    print("=" * 80)
    return manifest

if __name__ == "__main__":
    run_pipeline()
