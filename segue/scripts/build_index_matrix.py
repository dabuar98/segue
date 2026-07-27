"""
Build the feature vector space matrix that is used as FAISS index to compute similarity
Parameters:
    input_path (str):   The path to the JSON file containing clean track information
                        (Resulting from get_tracks pipeline)
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
from scripts.build_index_vector import build_index_vector

# Define data path
load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")
BUCKET_NAME = os.getenv("BUCKET_NAME")

def build_index_matrix(input_path):
    # Instantiate S3 client
    s3 = boto3.client('s3')

    # Read tracks.json
    with open(input_path) as json_file:
        tracks = json.load(json_file)

    # Resulting matrix
    # Create empty M x N matrix
    m = len(tracks) # Number of vectors
    n = 231 # Number of audio descriptors values
    result_mat = np.empty((m, n), dtype='float32')

    for idx, (id, metadata) in enumerate(tracks.items()):
        # Read file from bucket
        try:
            response = s3.get_object(
                Bucket=BUCKET_NAME,
                Key=f"audio_features/{id}.json"
            )
            data = json.load(response['Body'])
        except ClientError as e:
            print(f"[build_index_matrix][ERROR] - Error processing file {id}.json: {e}")
            continue

        # If data is loaded, build index vector and
        vector = build_index_vector(data) # Returns a 1 x D vector

        # Add vector as column in matrix (insertion order given by idx)
        result_mat[idx, :] = vector

    return result_mat