import numpy as np
from .extract_query_descriptors import extract_query_descriptors
from .utils import map_key_current_version, map_key_scale
from datetime import datetime

def build_query_vector_schedl(query_track):
    """
    Build a 1 x D vector where D is the dimension (number of descriptors) that is passed as query vector to compute
    similarity. The selection of the audio features is based on the descriptor set suggested by Schedl et al. [1]:
    key, key scale, key strength, harmonic pitch class profile, MFCCs (mean and variance), spectral centroid,
    rolloff, flux, zero-crossing rate, tempo, danceability, beats loudness, and onset rate.
    Args:
        query_track: Path to the query track (string)

    Returns:
        query_vector: 1 x D Numpy array containing the values of the audio descriptors

    References:
        [1]     M. Schedl, E. Gómez, and J. Urbano, "Music information retrieval: Recent developments and
                applications," Foundations and Trends in Information Retrieval, vol. 8, no. 2-3, pp. 127-261,
                2014.
    """
    # Compute audio descriptors
    descriptors = extract_query_descriptors(query_track)
    # Store descriptors in a list
    tmp_list = []

    # Add scalar tonal key values
    tmp_list.append(
        map_key_current_version(descriptors.get('tonal').get('key_edma').get('key'))
    )
    tmp_list.append(
        map_key_scale(descriptors.get('tonal').get('key_edma').get('scale'))
    )
    tmp_list.append(descriptors.get('tonal').get('key_edma').get('strength'))

    # Add 36 values from tonal.hpcp.mean
    for hpcp in descriptors.get('tonal').get('hpcp').get('mean'):
        tmp_list.append(hpcp)

    # Add low level descriptors
    # Add 13 values from lowlevel.mfcc.mean
    for mfccmean in descriptors.get('lowlevel').get('mfcc').get('mean'):
        tmp_list.append(mfccmean)

    # Add 13 values from diagonal of lowlevel.mfcc.cov
    mfcc_cov = descriptors.get('lowlevel').get('mfcc').get('cov')
    for i in range(len(mfcc_cov)):
        tmp_list.append(mfcc_cov[i][i])

    # Add scalar low-level values
    tmp_list.append(descriptors.get('lowlevel').get('spectral_centroid').get('mean'))
    tmp_list.append(descriptors.get('lowlevel').get('spectral_rolloff').get('mean'))
    tmp_list.append(descriptors.get('lowlevel').get('spectral_flux').get('mean'))
    tmp_list.append(descriptors.get('lowlevel').get('zerocrossingrate').get('mean'))
    tmp_list.append(descriptors.get('lowlevel').get('zerocrossingrate').get('var'))

    # Add rhythmical scalar values
    tmp_list.append(descriptors.get('rhythm').get('bpm'))
    tmp_list.append(descriptors.get('rhythm').get('danceability'))
    tmp_list.append(descriptors.get('rhythm').get('beats_loudness').get('mean'))
    tmp_list.append(descriptors.get('rhythm').get('beats_loudness').get('var'))
    tmp_list.append(descriptors.get('rhythm').get('onset_rate'))

    d = len(tmp_list) # Dimension of the vector
    # Instantiate empty a Numpy array
    query_vector = np.array(tmp_list, dtype='float32')
    # Transform array into a 1 x D
    query_vector = query_vector.reshape(1, d)

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildQueryVectorSchedl: Created a {query_vector.shape} vector")
    return query_vector

###### Executable ########
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DATA_PATH = os.getenv("DATA_PATH")
    vector = build_query_vector_schedl(f"{DATA_PATH}/miscellaneous/sample.mp3")
    print(vector)
