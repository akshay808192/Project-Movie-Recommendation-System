"""
Database Seeder
Populates the SQLite `movies` table with the processed MovieLens dataset metadata.
Preserves actual movie IDs from the dataset.
"""

import os
import sqlite3
import pandas as pd
from typing import Optional

from backend.app.utils.helpers import get_poster_url

PROCESSED_METADATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../data/processed/movies_metadata.csv")
)
FALLBACK_METADATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../data/movies_processed.csv")
)


def seed_movies(conn: sqlite3.Connection, force: bool = False) -> int:
    """
    Seed the `movies` table from the processed dataset CSV.
    Returns the count of seeded movies.
    """
    cursor = conn.cursor()

    # Check if movies are already seeded
    cursor.execute("SELECT COUNT(*) as cnt FROM movies")
    count = cursor.fetchone()[0]

    if count >= 9000 and not force:
        return count

    # Determine file path
    csv_path = PROCESSED_METADATA_PATH if os.path.exists(PROCESSED_METADATA_PATH) else FALLBACK_METADATA_PATH
    if not os.path.exists(csv_path):
        print(f"Warning: Metadata file not found at {csv_path}. Skipping seed.")
        return 0

    print(f"Seeding movies into SQLite from '{csv_path}'...")
    df = pd.read_csv(csv_path)

    movies_to_insert = []
    for _, row in df.iterrows():
        mid = int(row['movieId'])
        title = str(row['title'])
        clean_title = str(row['clean_title']) if ('clean_title' in row and pd.notna(row['clean_title'])) else title
        year = int(row['year']) if ('year' in row and pd.notna(row['year'])) else None
        
        genres = str(row['genres_joined']) if ('genres_joined' in row and pd.notna(row['genres_joined'])) else (
            str(row['genres']) if ('genres' in row and pd.notna(row['genres'])) else ""
        )
        tags = str(row['tags_joined']) if ('tags_joined' in row and pd.notna(row['tags_joined'])) else ""
        
        vote_count = int(row['vote_count']) if ('vote_count' in row and pd.notna(row['vote_count'])) else 0
        mean_rating = float(round(row['mean_rating'], 2)) if ('mean_rating' in row and pd.notna(row['mean_rating'])) else 0.0
        popularity_score = float(round(row['popularity_score'], 3)) if ('popularity_score' in row and pd.notna(row['popularity_score'])) else 0.0
        
        imdb_id = str(row['imdb_id_str']) if ('imdb_id_str' in row and pd.notna(row['imdb_id_str'])) else None
        tmdb_id = int(row['tmdb_id_int']) if ('tmdb_id_int' in row and pd.notna(row['tmdb_id_int'])) else None
        poster_url = get_poster_url(mid, tmdb_id)

        movies_to_insert.append((
            mid,
            title,
            clean_title,
            year,
            genres,
            tags,
            vote_count,
            mean_rating,
            popularity_score,
            imdb_id,
            tmdb_id,
            poster_url
        ))

    cursor.executemany("""
        INSERT INTO movies (
            movie_id, title, clean_title, year, genres, tags,
            vote_count, mean_rating, popularity_score, imdb_id, tmdb_id, poster_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(movie_id) DO UPDATE SET
            title = excluded.title,
            clean_title = excluded.clean_title,
            year = excluded.year,
            genres = excluded.genres,
            tags = excluded.tags,
            vote_count = excluded.vote_count,
            mean_rating = excluded.mean_rating,
            popularity_score = excluded.popularity_score,
            imdb_id = excluded.imdb_id,
            tmdb_id = excluded.tmdb_id,
            poster_url = excluded.poster_url
    """, movies_to_insert)

    conn.commit()
    print(f"Successfully seeded {len(movies_to_insert)} movies into SQLite database.")
    return len(movies_to_insert)
