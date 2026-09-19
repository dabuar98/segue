import json
import os
import boto3
import numpy as np
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from .build_index_vector_tzanetakis import build_index_vector_tzanetakis
from .build_index_vector_bogdanov import build_index_vector_bogdanov
from datetime import datetime

# Maps a descriptor set name to the vector-builder function used to compute each track's descriptors
VECTOR_BUILDERS = {
    'tzanetakis': build_index_vector_tzanetakis,
    'bogdanov': build_index_vector_bogdanov,
}

def build_index_matrix(tracks, n, descriptor_set='tzanetakis'):
    """
    Build the feature vector space matrix that is used as FAISS index to compute similarity
    Args:
        tracks: A string containing tracks information (string)
        n: The number of audio descriptors (integer)
        descriptor_set: Which descriptor set to build the vectors with, one of VECTOR_BUILDERS' keys (string)

    Returns:
        index matrix :  A M x N matrix representing the feature vector space used to feed FAISS where M is the number
                        of tracks and N is the dimension of each vector (number of descriptors)
    """
    vector_builder = VECTOR_BUILDERS[descriptor_set]
    total_processed = 0 # For stats
    # Instantiate S3 client
    s3 = boto3.client('s3')

    # Read tracks.json
    with open(tracks, 'r') as json_file:
        tracks = json.load(json_file)

    # Create empty M x N matrix
    m = len(tracks) # Number of vectors to create
    index_matrix = np.full((m, n), np.nan, dtype='float32')

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexMatrix: Starting to build index matrix")
    for idx, (id, metadata) in enumerate(tracks.items()):
        # Read file from bucket
        try:
            response = s3.get_object(
                Bucket=BUCKET_NAME,
                Key=f"audio_features/{id}.json"
            )
            data = json.load(response['Body'])
        except ClientError as e:
            print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ ERROR ] BuildIndexMatrix: Error processing file {id}.json, {e}")
            continue

        # If data is loaded, build index vector and
        vector = vector_builder(data) # Returns a 1 x D vector

        # Add vector as column in matrix (insertion order given by idx)
        index_matrix[idx, :] = vector
        total_processed += 1

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexMatrix: Processed {total_processed:,} files")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexMatrix: Created a {index_matrix.shape} feature vector space matrix")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexMatrix: {"There are values missing" if np.isnan(index_matrix).any() else "There are not values missing"}")

    # Save the index matrix as a separate binary numpy file
    with open (f"{DATA_PATH}/index_mat_{descriptor_set}.npy", "wb") as f:
        np.save(f, index_matrix)
    
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexMatrix: Index matrix binary exported")

    return index_matrix

###### Executable ########
if __name__ == "__main__":
    load_dotenv()
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DATA_PATH = os.getenv("DATA_PATH")
    #build_index_matrix(f"{DATA_PATH}/tracks.json", 28)
    build_index_matrix(f"{DATA_PATH}/tracks.json", 107, descriptor_set='bogdanov')

