# Movie Recommendation System Using Collaborative Filtering with Popularity-Based Cold Start

An end-to-end full-stack machine learning project built with Python, FastAPI, Scikit-Learn, and React.

---

## 1. Project Overview
This project is a comprehensive full-stack movie recommendation platform. It aims to deliver highly personalized movie recommendations to users by analyzing their past interactions (ratings, favorites, and watch history). To provide an immediate experience for new users, the system intelligently blends global popularity metrics with personalized collaborative filtering vectors.

## 2. Problem Statement
Modern streaming platforms struggle with information overload; users have too many choices and often fail to find content they enjoy. Furthermore, recommendation engines heavily suffer from the **Cold-Start Problem**—the inability to recommend accurate items to brand-new users because the system has no historical data on their preferences. 

## 3. Objectives
1. Build a robust Machine Learning recommendation engine based on real-world datasets.
2. Solve the new-user cold-start problem using statistical popularity metrics.
3. Provide a seamless, real-time transition from popularity-based recommendations to highly personalized collaborative filtering as the user interacts with the app.
4. Develop a premium, responsive, cinematic frontend interface.
5. Create a scalable backend API and database architecture capable of storing user interactions without latency.

## 4. Features
- **User Authentication**: Secure JWT-based registration and login.
- **Cinematic Frontend UI**: Dark mode, glassmorphism, responsive CSS grid, and smooth animations.
- **Interactive Catalog**: Search by title, filter by genres, and view detailed movie metadata.
- **User Interactions**: Rate movies (0.5 - 5 stars), add to favorites, and track watch history.
- **Dynamic Recommender**: Instantly hot-swaps the recommendation strategy (Cold Start ➔ Hybrid ➔ Collaborative) based on the exact number of movies a user has rated.
- **Explainable AI**: Provides transparency by explaining *why* a movie was recommended (e.g., "Because you loved 'The Matrix' (85% match)").

## 5. Technology Stack
- **Frontend**: React 19, Vite, Lucide-React (Icons), CSS3 (Glassmorphism & CSS Variables).
- **Backend**: FastAPI, Python 3.10+, Uvicorn, Pydantic (Data Validation).
- **Machine Learning**: Scikit-Learn (Cosine Similarity), SciPy (Sparse Matrices), NumPy, Pandas.
- **Database**: SQLite (Relational SQL for users, movies, and interactions).

## 6. System Architecture
1. **Data Layer**: Raw MovieLens data is parsed, cleaned, and seeded into a SQLite database.
2. **Machine Learning Layer**: An offline pipeline trains an Item-to-Item similarity matrix and exports artifacts (Pickle dictionaries).
3. **API Layer**: A FastAPI server loads the ML artifacts into memory on startup and serves real-time inference via RESTful endpoints.
4. **Client Layer**: A React Single Page Application (SPA) consumes the APIs and renders the UI dynamically.

## 7. Dataset Description
The system is built on the official **MovieLens 100K** dataset (`ml-latest-small`). It contains real user interactions without any fabricated data:
- **Unique Users:** 610
- **Unique Movies:** 9,742
- **Total Ratings:** 100,836
- **Rating Matrix Sparsity:** 98.30%
- **Metadata**: Includes release years, genres, and cross-reference links (IMDb/TMDb).

## 8. Data Preprocessing
To prepare the dataset for the collaborative filtering model:
1. Removed duplicate or malformed rows.
2. Handled missing titles and extracted release years using regex.
3. Filtered out movies with zero ratings to prevent division-by-zero errors.
4. Mapped arbitrary string IDs to contiguous integer indices to optimize sparse matrix memory allocation.
5. Applied **User-Mean Centering** (subtracting a user's average rating from all their ratings) to normalize harsh vs. lenient raters.

## 9. Popularity-Based Recommendation
To identify objectively "good" movies for general audiences, we implemented the **IMDb Bayesian Weighted Rating (WR)** formula:
`WR = (v / (v+m)) * R + (m / (v+m)) * C`
- `v`: Number of votes for the movie.
- `m`: Minimum vote threshold (80th percentile of rated movies = 12 votes).
- `R`: Average rating of the movie.
- `C`: Global mean rating across the entire dataset (3.50).

## 10. Collaborative Filtering
For personalized recommendations, we use **Item-to-Item Collaborative Filtering**:
1. A sparse User-Item matrix is constructed from centered ratings.
2. A Cosine Similarity matrix is computed across all 9,742 items.
3. When a user requests recommendations, the system looks at the movies they rated highly (>= 3.5 stars) and finds the mathematical "nearest neighbors" in the item similarity graph.

## 11. Cold-Start Problem
When a user first registers, they have 0 interactions in the database. A traditional Collaborative Filtering model would fail (throw an error or return random noise). To solve this, the system detects users with 0 ratings and routes them to the Popularity-Based Recommendation engine, serving high-confidence blockbusters.

## 12. Hybrid Recommendation Strategy
As the user provides their first few ratings (1 to 4 interactions), the system uses an **Adaptive Hybrid Strategy**. It computes a blended score:
`Score = α * NormalizedCF + (1 - α) * NormalizedPopularity`
Where `α = (interaction count / 5.0)`. This smoothly transitions the feed from global popularity to localized personalization. Once the user hits 5 ratings, it relies purely on Collaborative Filtering.

## 13. Model Training
The training pipeline (`ml/training/train.py`) executes the following operations:
1. Loads the preprocessed ratings dataframe.
2. Computes the dense Cosine Similarity matrix efficiently.
3. Extracts the top-100 most similar neighbors for each movie.
4. Saves this heavily truncated, lightweight dictionary (`recommender_artifacts.pkl`) to disk.
This ensures the live backend requires very little RAM and computes recommendations in under 1 millisecond.

## 14. Evaluation Metrics
The system is rigorously evaluated using a **Per-User Temporal Split (80% Train / 20% Test)** to prevent future-data leakage. The metrics used are:
- **Precision@K**: Proportion of recommended items in the top-K that are relevant.
- **Recall@K**: Proportion of relevant items that were successfully recommended in the top-K.
- **Hit Rate@K**: Percentage of users who had at least 1 relevant recommendation in their top-K.
- **MAP@K**: Mean Average Precision, taking ranking order into account.

## 15. Results
Based on our isolated test evaluations (`K=10`):
- **Popularity Baseline**: Precision: 0.0481, Hit Rate: 28.62%
- **Collaborative Filtering**: Precision: 0.0465, Hit Rate: 30.13%
- **Hybrid Recommender**: Precision: **0.0660**, Hit Rate: **35.35%**

The Hybrid approach decisively outperforms the static baselines, proving that blending collaborative vectors with global popularity yields the best consumer experience.

## 16. Backend API
The FastAPI backend exposes the following RESTful routes:
- `POST /api/users/register` & `POST /api/users/login`
- `GET /api/movies/popular` & `GET /api/movies/search` (Case-insensitive & paginated)
- `GET /api/recommendations/me` (Core engine endpoint)
- `POST /api/interactions/rating`, `POST /api/interactions/like`

## 17. Frontend Architecture
The React application follows a modular component structure:
- **App.jsx**: Global layout and tab-based routing (avoiding heavy external router dependencies).
- **MovieCard.jsx**: Interactive component handling hover scale, rating interactions, and metadata display.
- **ToastContext.jsx**: Global state provider for rendering error and success notifications beautifully over the UI.

## 18. Database Design
SQLite is used with the following core tables:
- `users`: id, username, email, hashed_password
- `movies`: movie_id, title, genres, popularity_score
- `ratings`: user_id, movie_id, rating
- `likes`: user_id, movie_id (Bookmarks)

## 19. Installation
### Prerequisites
- Python 3.10+
- Node.js v18+ and npm

### Install Dependencies
```powershell
# Backend Dependencies
pip install -r backend/requirements.txt

# Frontend Dependencies
cd frontend
npm install
cd ..
```

## 20. How to Run
Open two separate PowerShell windows.

**Terminal 1 (Backend Server):**
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 (Frontend Server):**
```powershell
cd frontend
npm run dev
```
Navigate to `http://localhost:5173` in your browser.

## 21. How to Train Model
To run the evaluation benchmarks from scratch and test the algorithms:
```powershell
python backend/scripts/evaluate.py
```

## 22. How to Retrain Model
As users interact with the app, their preferences are saved to the database. To ingest these new interactions and update the global similarity matrix, run the orchestration script:
```powershell
python ml/training/retrain.py
```
This automatically runs preprocessing, matrix computation, artifact generation, and evaluation reporting sequentially.

## 23. Screenshots
*(Add screenshots of the Home page, Movie Details modal, Search interface, and Onboarding flow here)*

## 24. Future Scope
- **Content-Based Filtering**: Integrate NLP (TF-IDF) on movie descriptions and cast metadata to handle newly added items (Item Cold Start).
- **Matrix Factorization**: Implement Singular Value Decomposition (SVD) or Neural Collaborative Filtering to capture deeper latent semantic relationships.
- **Cloud Deployment**: Containerize the app via Docker and deploy to AWS or Heroku using PostgreSQL.

## 25. Limitations
- **Item Cold-Start**: If a brand-new movie is added to the database with 0 ratings, Collaborative Filtering cannot recommend it to anyone until at least a few users rate it.
- **Memory Scaling**: The current script computes a full `N x N` dense matrix during training. While fine for 9,700 movies, scaling to 100,000+ movies would require Spark or approximate nearest neighbor algorithms (e.g., FAISS).
