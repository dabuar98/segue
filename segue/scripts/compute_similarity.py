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
import faiss
from dotenv import load_dotenv
from build_query_vector import build_query_vector

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")
path_index = f"{DATA_PATH}/index.faiss"

def compute_similarity(query, n=20):
    # Load index
    faiss_index = faiss.read_index(path_index)
    # Build query vector from track's audio descriptors
    query_vector = build_query_vector(query)
    distances, indices = faiss_index.search(query_vector, n)
    return distances, indices
