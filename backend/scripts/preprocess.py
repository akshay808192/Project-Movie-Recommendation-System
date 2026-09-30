"""
Backend wrapper to run data preprocessing
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ml.preprocessing.preprocess import run_pipeline

if __name__ == "__main__":
    run_pipeline()
