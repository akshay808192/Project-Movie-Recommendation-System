"""
Authentication Service
Handles user registration, login, password verification, and JWT user resolution.
"""

import sqlite3
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.app.database.connection import get_db
from backend.app.database import crud
from backend.app.schemas.schemas import UserRegister, UserLogin, UserOut
from backend.app.utils.helpers import hash_password, verify_password, create_access_token, decode_access_token

security = HTTPBearer(auto_error=False)


def register_user(db: sqlite3.Connection, user_data: UserRegister) -> dict:
    """Register a new user in SQLite."""
    # Check if username or email exists
    if crud.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken."
        )
    if crud.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered."
        )

    hashed_pw = hash_password(user_data.password)
    user_row = crud.create_user(db, user_data.username, user_data.email, hashed_pw)

    user_out = UserOut(
        id=user_row['id'],
        username=user_row['username'],
        email=user_row['email'],
        created_at=str(user_row['created_at'])
    )

    access_token = create_access_token(data={"sub": str(user_out.id), "username": user_out.username})
    return {"access_token": access_token, "token_type": "bearer", "user": user_out}


def login_user(db: sqlite3.Connection, login_data: UserLogin) -> dict:
    """Authenticate user with username or email identifier."""
    identifier = login_data.identifier
    user_row = crud.get_user_by_identifier(db, identifier)
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    if not verify_password(login_data.password, user_row['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    user_out = UserOut(
        id=user_row['id'],
        username=user_row['username'],
        email=user_row['email'],
        created_at=str(user_row['created_at'])
    )

    access_token = create_access_token(data={"sub": str(user_out.id), "username": user_out.username})
    return {"access_token": access_token, "token_type": "bearer", "user": user_out}


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: sqlite3.Connection = Depends(get_db)
) -> UserOut:
    """FastAPI dependency requiring a valid Bearer token."""
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required."
        )

    payload = decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token."
        )

    user_id = int(payload["sub"])
    user_row = crud.get_user_by_id(db, user_id)
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists."
        )

    return UserOut(
        id=user_row['id'],
        username=user_row['username'],
        email=user_row['email'],
        created_at=str(user_row['created_at'])
    )


def get_optional_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: sqlite3.Connection = Depends(get_db)
) -> Optional[UserOut]:
    """FastAPI dependency that allows unauthenticated/guest users."""
    if not auth:
        return None

    payload = decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        return None

    try:
        user_id = int(payload["sub"])
        user_row = crud.get_user_by_id(db, user_id)
        if not user_row:
            return None
        return UserOut(
            id=user_row['id'],
            username=user_row['username'],
            email=user_row['email'],
            created_at=str(user_row['created_at'])
        )
    except Exception:
        return None
