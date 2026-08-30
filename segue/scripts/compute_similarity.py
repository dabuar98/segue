"""
This script retrieves the N-most similar tracks to a query track
Parameters:
    - query_vector
    - n (int): The number of tracks to return (Default 20)
Returns:
    - D (np.array): Distances
    - I (np.array): Indices
"""

import os
import sys
from pathlib import Path
import faiss
import joblib
from dotenv import load_dotenv

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")

def compute_similarity(query_vector, n=20):

    # Load index
    faiss_index = faiss.read_index(f"{DATA_PATH}/index.faiss")

    # Load scaler
    scaler = joblib.load(f"{DATA_PATH}/index_scaler.joblib")

    # Apply scaler to query vector
    query_vector = scaler.transform(query_vector)

    # Search n-similar vectors
    distances, indices = faiss_index.search(query_vector, n)
    return distances, indices
