"""
Build the feature vector space matrix that is used as FAISS index to compute similarity
Parameters:
    input_path (str):   The path to the JSON file containing clean track information
                        (Resulting from get_tracks pipeline)
    n (int): Number of audio descriptors
Returns:
    result (np.darray): A M x N matrix representing the feature vector space used to feed FAISS
                        where M is the number of vectors (156,133 tracks) and N is the dimension of each vector (231 audio descriptors)

"""
import json
import os
import boto3
import numpy as np
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from build_index_vector import build_index_vector
from datetime import datetime

# # Get bucket name
# load_dotenv()
# BUCKET_NAME = os.getenv("BUCKET_NAME")
# DATA_PATH = os.getenv("DATA_PATH")

def build_index_matrix(input_path, n):
    total_processed = 0 # For stats
    # Instantiate S3 client
    s3 = boto3.client('s3')

    # Read tracks.json
    with open(input_path) as json_file:
        tracks = json.load(json_file)

    # Resulting matrix
    # Create empty M x N matrix
    m = len(tracks) # Number of vectors
    result_mat = np.full((m, n), np.nan ,dtype='float32')

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
            print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ ERROR ] BuildIndexMatrix: Error processing file {id}.json: {e}")
            continue

        # If data is loaded, build index vector and
        vector = build_index_vector(data) # Returns a 1 x D vector

        # Add vector as column in matrix (insertion order given by idx)
        result_mat[idx, :] = vector
        total_processed += 1

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexMatrix: Processed {total_processed:,} files")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexMatrix: Created a {result_mat.shape} feature vector space matrix")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexMatrix: {"There are values missing" if np.isnan(result_mat).any() else "There are not values missing"}")

    # Save the index matrix as a separate binary numpy file
    with open (f"{DATA_PATH}/index_mat.npy", "wb") as f:
        np.save(f, result_mat)
    
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexMatrix: Index matrix binary exported")

    return result_mat

###### Executable ########
if __name__ == "__main__":
    load_dotenv()
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DATA_PATH = os.getenv("DATA_PATH")
    build_index_matrix(f"{DATA_PATH}/tracks.json", 75)
    # build_index_matrix(f"{DATA_PATH}/tracks_min.json")
