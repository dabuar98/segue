"""
This script retrieves the N-most similar tracks to a query track
Parameters:
    - query (string): Path to the query track
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

# Execute it from /segue
sys.path.append(str(Path(__file__).resolve().parent))
from build_query_vector import build_query_vector

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")

def compute_similarity(query, n=20):
    # Load index
    faiss_index = faiss.read_index(f"{DATA_PATH}/index.faiss")
    # Load scaler
    scaler = joblib.load(f"{DATA_PATH}/index_scaler.joblib")
    # Build query vector from track's audio descriptors
    query_vector = build_query_vector(query)

    # Normalise query vector
    query_vector = scaler.transform(query_vector)

    # Search n-similar vectors
    distances, indices = faiss_index.search(query_vector, n)
    return distances, indices
