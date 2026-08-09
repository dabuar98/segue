"""
Generate the FAISS index used to compute similarity. Following Linden et al. [1], the index produced in this script
is stored for offline similarity computation.
Parameter:
    - index_mat (string): Path to index_mat.npy
Returns: None
References:
    [1] Linden, G., Smith, B. and York, J. (2003)
        'Amazon.com recommendations: Item-to-item collaborative filtering',
        IEEE Internet Computing, 7(1), pp. 76–80. doi: 10.1109/MIC.2003.1167344.

"""
from datetime import datetime
import faiss
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
import os
from sklearn.preprocessing import StandardScaler
import joblib

def build_index(index_mat):
    d = 231  # Dimension (Number of audio descriptors values)
    index_mat = Path(index_mat)
    # Load index matrix .npy
    index = np.load(index_mat)

    # Normalise index so audio features have 0 mean and standard deviation of 1
    scaler = StandardScaler()
    index = scaler.fit_transform(index)

    # Export scaler to normalise query vector
    joblib.dump(scaler, f"{DATA_PATH}/index_scaler.joblib")

    faiss_index = faiss.IndexFlatL2(d)  # build the index
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndex: Start building faiss index")
    faiss_index.add(index)  # add vectors to the index
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndex: {faiss_index.ntotal:,} vectors added to faiss index")
    # Store index for offline computation
    faiss.write_index(faiss_index, f"{DATA_PATH}/index.faiss")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndex: Index exported")

##### Executable ######
if __name__ == "__main__":
    load_dotenv()
    DATA_PATH = os.getenv("DATA_PATH")
    path_index = f"{DATA_PATH}/index_mat.npy"
    build_index(path_index)

