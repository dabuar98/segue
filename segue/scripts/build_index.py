from datetime import datetime
import faiss
import numpy as np
from dotenv import load_dotenv
import os
from sklearn.preprocessing import StandardScaler
import joblib

def build_index(index_mat):
    """
    Generate the FAISS index used to compute similarity. Following Linden et al. [1], the index produced in this script
    is stored for offline similarity computation.
    Args:
        index_mat: Index matrix (NumPy binary)
        n: Number of audio descriptors (integer)

    Returns:
        None
    """
    # Load index matrix .npy
    raw_vectors = np.load(index_mat)

    # Normalise index so audio features have 0 mean and standard deviation of 1
    scaler = StandardScaler()
    vectors = scaler.fit_transform(raw_vectors)

    # Normalise vectors
    faiss.normalize_L2(vectors)

    # Build index
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndex: Start building faiss index")
    faiss_index = faiss.IndexFlatIP(vectors.shape[1])
    # faiss_index = faiss.IndexFlat(vectors.shape[1])

    # Add vectors to index
    faiss_index.add(vectors)
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndex: {faiss_index.ntotal:,} vectors added to faiss index")

    # Store index for offline computation
    faiss.write_index(faiss_index, f"{DATA_PATH}/index.faiss")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndex: Index exported")

    # Export scaler to normalise query vector
    joblib.dump(scaler, f"{DATA_PATH}/index_scaler.joblib")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndex: Scaler exported")

##### Executable ######
if __name__ == "__main__":
    load_dotenv()
    DATA_PATH = os.getenv("DATA_PATH")
    build_index(f"{DATA_PATH}/index_mat_tzanetakis.npy")

