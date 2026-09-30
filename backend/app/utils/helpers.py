"""
Authentication Helpers, Password Hashing, JWT Tokens, and Poster Resolution
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import jwt
from dotenv import load_dotenv

load_dotenv()

# JWT Configurations
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "cinematic-movie-recommender-secure-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

# --- Password Hashing with PBKDF2-HMAC-SHA256 ---
def hash_password(password: str) -> str:
    """Hash password with secure salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return f"{salt}:{pw_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored salt:hash."""
    try:
        salt, stored_hash = hashed_password.split(":")
        calc_hash = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return secrets.compare_digest(calc_hash, stored_hash)
    except Exception:
        return False

# --- JWT Token Handling ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Encode JWT access token with payload and expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# --- Curated High-Quality TMDB Poster URLs for Top Classic & Popular Titles ---
CURATED_POSTERS: Dict[int, str] = {
    1: "https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg", # Toy Story
    2: "https://image.tmdb.org/t/p/w500/vgpXjv1vVsFsYvtPv891qq8NzYl.jpg", # Jumanji
    6: "https://image.tmdb.org/t/p/w500/zMyfPUelumio3tiDKMi0qnv49Ki.jpg", # Heat
    47: "https://image.tmdb.org/t/p/w500/6yoghtyTpznpBik8EngEmJsk9UO.jpg", # Se7en
    50: "https://image.tmdb.org/t/p/w500/961ghSmQ6bHw6QjG9L7n20X4H2f.jpg", # The Usual Suspects
    110: "https://image.tmdb.org/t/p/w500/or1gBugydmjToAEqDpHTj7MiY4b.jpg", # Braveheart
    260: "https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg", # Star Wars IV
    296: "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", # Pulp Fiction
    318: "https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg", # Shawshank Redemption
    356: "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", # Forrest Gump
    527: "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg", # Schindler's List
    588: "https://image.tmdb.org/t/p/w500/yA07Gk2k9sT86HjHkC4Qz3QoPq5.jpg", # Aladdin
    589: "https://image.tmdb.org/t/p/w500/5M0j0B18abtBI5em2mNO1IHLoUN.jpg", # Terminator 2
    593: "https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg", # Silence of the Lambs
    858: "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", # The Godfather
    1196: "https://image.tmdb.org/t/p/w500/2l05TqMFGQrmfmSk7umQRIbsHC9.jpg", # Star Wars V
    1198: "https://image.tmdb.org/t/p/w500/4p1N2Qrt8j0Tl8SWg2ZISMT8TeP.jpg", # Raiders of the Lost Ark
    1210: "https://image.tmdb.org/t/p/w500/mDCBQNmRkJFvh0q0c51x2uR0U8e.jpg", # Star Wars VI
    1213: "https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg", # Goodfellas
    1221: "https://image.tmdb.org/t/p/w500/hek3koDUyMrk7uOBvImvT21BInD.jpg", # The Godfather Part II
    2571: "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", # The Matrix
    2959: "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg", # Fight Club
    3114: "https://image.tmdb.org/t/p/w500/3GkstWj8mFjB9CqWfFh28t6vNq0.jpg", # Toy Story 2
    4993: "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cDK6.jpg", # Fellowship of the Ring
    5952: "https://image.tmdb.org/t/p/w500/5VTN0pR8gcqV3EPUHHfMGnJYN9L.jpg", # Two Towers
    7153: "https://image.tmdb.org/t/p/w500/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg", # Return of the King
    58559: "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg", # The Dark Knight
    79132: "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg", # Inception
    109487: "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", # Interstellar
    260: "https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg"
}

GENRE_GRADIENTS = {
    "Action": "from-red-600/30 to-amber-700/30",
    "Adventure": "from-amber-600/30 to-emerald-700/30",
    "Animation": "from-pink-600/30 to-purple-700/30",
    "Children": "from-yellow-500/30 to-blue-500/30",
    "Comedy": "from-yellow-600/30 to-orange-700/30",
    "Crime": "from-zinc-700/40 to-red-900/40",
    "Documentary": "from-teal-600/30 to-cyan-800/30",
    "Drama": "from-blue-700/30 to-indigo-900/30",
    "Fantasy": "from-purple-600/30 to-fuchsia-800/30",
    "Film-Noir": "from-stone-900/60 to-zinc-800/60",
    "Horror": "from-rose-950/50 to-stone-900/60",
    "Musical": "from-violet-600/30 to-pink-700/30",
    "Mystery": "from-slate-700/40 to-purple-950/40",
    "Romance": "from-rose-500/30 to-pink-700/30",
    "Sci-Fi": "from-cyan-600/30 to-blue-900/30",
    "Thriller": "from-emerald-700/30 to-slate-900/40",
    "War": "from-stone-700/40 to-amber-900/40",
    "Western": "from-amber-700/40 to-yellow-900/40"
}

def get_poster_url(movie_id: int, tmdb_id: Optional[int] = None) -> Optional[str]:
    """Return verified poster URL if available or None."""
    if movie_id in CURATED_POSTERS:
        return CURATED_POSTERS[movie_id]
    return None

def get_imdb_url(imdb_id_str: Optional[str]) -> Optional[str]:
    """Format full IMDb web link."""
    if imdb_id_str:
        return f"https://www.imdb.com/title/{imdb_id_str}/"
    return None
