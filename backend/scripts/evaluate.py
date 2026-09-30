"""
Backend wrapper to run model evaluation
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ml.evaluation.evaluate import run_evaluation

if __name__ == "__main__":
    run_evaluation()
