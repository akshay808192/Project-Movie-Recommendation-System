"""
Movie Recommendation System - FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database.connection import init_db
from backend.app.recommender.engine import RecommenderEngine
from backend.app.services.recommendation_service import get_engine
from backend.app.api.auth import router as auth_router
from backend.app.api.users import router as users_router
from backend.app.api.movies import router as movies_router
from backend.app.api.recommendations import router as recs_router
from backend.app.api.interactions import router as interactions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite tables and preload ML Recommender Engine
    print("Initializing Database...")
    init_db()
    print("Pre-loading ML Recommender Engine Artifacts...")
    RecommenderEngine.get_instance()
    get_engine()
    print("FastAPI Application Ready!")
    yield
    print("Shutting down...")


app = FastAPI(
    title="Movie Recommendation System API",
    description="Collaborative Filtering Recommender with Popularity-Based Cold Start (FastAPI + ML)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Vite React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from Vite React app or any client during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(users_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(movies_router, prefix="/api")
app.include_router(recs_router, prefix="/api")
app.include_router(interactions_router, prefix="/api")


@app.get("/", tags=["General"])
def root():
    return {
        "status": "online",
        "service": "Movie Recommendation System API",
        "algorithm": "Item-to-Item Collaborative Filtering + Bayesian Popularity Cold-Start",
        "docs_url": "/docs"
    }


@app.get("/api/health", tags=["General"])
def health_check():
    return {
        "status": "healthy",
        "database": "sqlite",
        "engine_loaded": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
