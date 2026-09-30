@echo off
echo ============================================================
echo Starting CineMatch AI Backend (FastAPI + Uvicorn)
echo API URL: http://127.0.0.1:8000
echo Docs:    http://127.0.0.1:8000/docs
echo ============================================================
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
