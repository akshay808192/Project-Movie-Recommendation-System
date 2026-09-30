"""
Database CRUD Operations for SQLite
Cleanly encapsulates all database transactions across:
- users
- movies
- ratings / user_ratings
- likes / favorites / user_favorites
- watch_history / user_history
"""

import sqlite3
from typing import Optional, List, Dict, Any, Tuple


# ==============================================================================
# User CRUD
# ==============================================================================

def get_user_by_id(db: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user record by primary key ID."""
    cursor = db.cursor()
    cursor.execute("SELECT id, username, email, hashed_password, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_user_by_username(db: sqlite3.Connection, username: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by username."""
    cursor = db.cursor()
    cursor.execute("SELECT id, username, email, hashed_password, created_at FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_user_by_email(db: sqlite3.Connection, email: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by email."""
    cursor = db.cursor()
    cursor.execute("SELECT id, username, email, hashed_password, created_at FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_user_by_identifier(db: sqlite3.Connection, identifier: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by matching either username or email."""
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, username, email, hashed_password, created_at FROM users WHERE username = ? OR email = ?",
        (identifier, identifier)
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def create_user(db: sqlite3.Connection, username: str, email: str, hashed_password: str) -> Dict[str, Any]:
    """Insert a new user record into the users table."""
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
        (username, email, hashed_password)
    )
    db.commit()
    user_id = cursor.lastrowid
    return get_user_by_id(db, user_id)


# ==============================================================================
# Movie CRUD
# ==============================================================================

def get_movie_by_id(db: sqlite3.Connection, movie_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve movie record from SQLite database by actual dataset movie_id."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT movie_id, title, clean_title, year, genres, tags,
               vote_count, mean_rating, popularity_score, imdb_id, tmdb_id, poster_url, created_at
        FROM movies WHERE movie_id = ?
    """, (movie_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def count_movies(db: sqlite3.Connection) -> int:
    """Count total movies stored in SQLite."""
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM movies")
    return cursor.fetchone()[0]


def get_popular_movies_from_db(
    db: sqlite3.Connection,
    genre: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Tuple[List[Dict[str, Any]], int]:
    """Retrieve paginated popular movies from SQLite."""
    cursor = db.cursor()
    if genre:
        cursor.execute("SELECT COUNT(*) FROM movies WHERE genres LIKE ?", (f"%{genre}%",))
        total = cursor.fetchone()[0]
        cursor.execute("""
            SELECT movie_id, title, clean_title, year, genres, tags,
                   vote_count, mean_rating, popularity_score, imdb_id, tmdb_id, poster_url
            FROM movies WHERE genres LIKE ?
            ORDER BY popularity_score DESC
            LIMIT ? OFFSET ?
        """, (f"%{genre}%", limit, offset))
    else:
        cursor.execute("SELECT COUNT(*) FROM movies")
        total = cursor.fetchone()[0]
        cursor.execute("""
            SELECT movie_id, title, clean_title, year, genres, tags,
                   vote_count, mean_rating, popularity_score, imdb_id, tmdb_id, poster_url
            FROM movies
            ORDER BY popularity_score DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

    rows = [dict(r) for r in cursor.fetchall()]
    return rows, total


# ==============================================================================
# Ratings CRUD
# ==============================================================================

def save_rating(db: sqlite3.Connection, user_id: int, movie_id: int, rating: float) -> Dict[str, Any]:
    """
    Insert or update a movie rating in both ratings and user_ratings tables.
    Also automatically adds the movie to watch_history and user_history.
    """
    cursor = db.cursor()
    # Save into primary ratings table
    cursor.execute("""
        INSERT INTO ratings (user_id, movie_id, rating, created_at, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, movie_id) DO UPDATE SET rating = excluded.rating, updated_at = CURRENT_TIMESTAMP
    """, (user_id, movie_id, rating))

    # Sync with user_ratings table
    cursor.execute("""
        INSERT INTO user_ratings (user_id, movie_id, rating, created_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, movie_id) DO UPDATE SET rating = excluded.rating, created_at = CURRENT_TIMESTAMP
    """, (user_id, movie_id, rating))

    # Also record into watch history
    cursor.execute("""
        INSERT INTO watch_history (user_id, movie_id, watched_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (user_id, movie_id))
    cursor.execute("""
        INSERT INTO user_history (user_id, movie_id, watched_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (user_id, movie_id))

    db.commit()
    return {"user_id": user_id, "movie_id": movie_id, "rating": rating}


def delete_rating(db: sqlite3.Connection, user_id: int, movie_id: int) -> bool:
    """Delete a user's rating for a specific movie."""
    cursor = db.cursor()
    cursor.execute("DELETE FROM ratings WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
    cursor.execute("DELETE FROM user_ratings WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
    db.commit()
    return cursor.rowcount > 0


def get_user_ratings(db: sqlite3.Connection, user_id: int) -> List[Dict[str, Any]]:
    """Retrieve all ratings submitted by a user, ordered latest first."""
    cursor = db.cursor()
    cursor.execute(
        "SELECT movie_id, rating, created_at FROM ratings WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    if not rows:
        # Fallback check
        cursor.execute(
            "SELECT movie_id, rating, created_at FROM user_ratings WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
    return [dict(r) for r in rows]


def get_all_new_ratings(db: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Retrieve all user ratings for periodic model retraining."""
    cursor = db.cursor()
    cursor.execute("SELECT user_id, movie_id, rating, created_at FROM ratings ORDER BY created_at ASC")
    return [dict(r) for r in cursor.fetchall()]


# ==============================================================================
# Likes / Favorites CRUD
# ==============================================================================

def toggle_favorite(db: sqlite3.Connection, user_id: int, movie_id: int) -> Tuple[bool, str]:
    """
    Toggle a movie in the user's likes/favorites list across both likes and user_favorites tables.
    Returns (is_liked, message).
    """
    cursor = db.cursor()
    cursor.execute("SELECT id FROM likes WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("DELETE FROM likes WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
        cursor.execute("DELETE FROM user_favorites WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
        db.commit()
        return False, "Removed from favorites."
    else:
        cursor.execute(
            "INSERT INTO likes (user_id, movie_id, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (user_id, movie_id)
        )
        cursor.execute(
            "INSERT INTO user_favorites (user_id, movie_id, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (user_id, movie_id)
        )
        db.commit()
        return True, "Added to favorites."


def get_user_favorites(db: sqlite3.Connection, user_id: int) -> List[Dict[str, Any]]:
    """Retrieve all favorite/liked movies for a user."""
    cursor = db.cursor()
    cursor.execute(
        "SELECT movie_id, created_at FROM likes WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    if not rows:
        cursor.execute(
            "SELECT movie_id, created_at FROM user_favorites WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
    return [dict(r) for r in rows]


# ==============================================================================
# Watch History CRUD
# ==============================================================================

def add_watch_history(db: sqlite3.Connection, user_id: int, movie_id: int) -> Dict[str, Any]:
    """Log a movie into watch_history and user_history."""
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO watch_history (user_id, movie_id, watched_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
        (user_id, movie_id)
    )
    cursor.execute(
        "INSERT INTO user_history (user_id, movie_id, watched_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
        (user_id, movie_id)
    )
    db.commit()
    cursor.execute("SELECT datetime('now') as now_str")
    now_str = cursor.fetchone()['now_str']
    return {"user_id": user_id, "movie_id": movie_id, "watched_at": now_str}


def get_user_watch_history(db: sqlite3.Connection, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve distinct watch history records for a user, ordered latest first."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT movie_id, MAX(watched_at) as last_watched
        FROM watch_history
        WHERE user_id = ?
        GROUP BY movie_id
        ORDER BY last_watched DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    if not rows:
        cursor.execute("""
            SELECT movie_id, MAX(watched_at) as last_watched
            FROM user_history
            WHERE user_id = ?
            GROUP BY movie_id
            ORDER BY last_watched DESC
            LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
    return [dict(r) for r in rows]


# ==============================================================================
# Interaction Counts
# ==============================================================================

def get_interaction_counts(db: sqlite3.Connection, user_id: int) -> Dict[str, int]:
    """Get interaction totals (ratings, favorites, history) for a user."""
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM ratings WHERE user_id = ?", (user_id,))
    total_ratings = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM likes WHERE user_id = ?", (user_id,))
    total_favorites = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM watch_history WHERE user_id = ?", (user_id,))
    total_history = cursor.fetchone()['cnt']

    return {
        "ratings": total_ratings,
        "favorites": total_favorites,
        "history": total_history,
        "total": total_ratings + total_favorites
    }
