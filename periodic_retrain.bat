@echo off
echo ============================================================
echo   Periodic Recommender Retraining Pipeline
echo   Incorporating Live SQLite Interactions into Recommender
echo ============================================================
python ml/training/periodic_retrain.py --force
pause
