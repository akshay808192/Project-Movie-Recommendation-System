"""
Authentication Endpoints
"""

import sqlite3
from fastapi import APIRouter, Depends
from backend.app.database.connection import get_db
from backend.app.schemas.schemas import UserRegister, UserLogin, TokenResponse, UserOut
from backend.app.services.auth_service import register_user, login_user, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: sqlite3.Connection = Depends(get_db)):
    """Register a new user and receive JWT access token."""
    return register_user(db, user_data)

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    """Authenticate and obtain JWT access token."""
    return login_user(db, login_data)

@router.get("/me", response_model=UserOut)
def get_me(current_user: UserOut = Depends(get_current_user)):
    """Get profile information for the authenticated user."""
    return current_user
