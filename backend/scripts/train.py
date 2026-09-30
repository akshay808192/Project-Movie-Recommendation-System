"""
Backend wrapper to run model training
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ml.training.train import train_recommender

if __name__ == "__main__":
    train_recommender()
