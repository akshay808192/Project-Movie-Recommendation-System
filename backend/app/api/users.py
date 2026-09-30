"""
Users Endpoints
Handles user registration, login, and user-specific history.
"""

import sqlite3
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, HTTPException, status
from backend.app.database.connection import get_db
from backend.app.database import crud
from backend.app.schemas.schemas import (
    UserRegister, UserLogin, TokenResponse, HistoryOut
)
from backend.app.services.auth_service import register_user, login_user
from backend.app.services.interaction_service import get_user_watch_history_list

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: sqlite3.Connection = Depends(get_db)):
    """
    Register a new user account.
    Returns JWT access token and user information.
    """
    return register_user(db, user_data)


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    """
    Authenticate an existing user using username or email and password.
    Returns JWT access token and user profile.
    """
    return login_user(db, login_data)


@router.get("/{user_id}/history", response_model=List[HistoryOut])
def get_user_history_by_id(
    user_id: int = Path(..., description="The ID of the user"),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieve the watch history of a specific user.
    Returns list of movies watched with timestamps and metadata.
    """
    # Verify user exists
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found."
        )

    return get_user_watch_history_list(db, user_id, limit=50)
