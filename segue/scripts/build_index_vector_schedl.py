import json
import os
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from .utils import map_key_former_version, map_key_scale

def build_index_vector_schedl(af_dict):
    """
    Create an 1 xD array with the audio features values retrieved for a mbid.
    The selection of the audio features is based on the descriptor set suggested by Schedl et al. [1]: key,
    key scale, key strength, harmonic pitch class profile, MFCCs (mean and variance), spectral centroid,
    rolloff, flux, zero-crossing rate, tempo, danceability, beats loudness, and onset rate.
    Args:
        af_dict (dict): A dict representation of the audio features

    Returns:
        result (nparray): A 1 x D Numpy array containing the values of the audio descriptors

    References:
        [1]     M. Schedl, E. Gómez, and J. Urbano, "Music information retrieval: Recent developments and
                applications," Foundations and Trends in Information Retrieval, vol. 8, no. 2-3, pp. 127-261,
                2014.
    """
    # Store descriptors in a list
    tmp_list = []

    # Add scalar tonal key values (former version)
    tmp_list.append(
        map_key_former_version(af_dict.get('tonal').get('key_key'))
    )
    tmp_list.append(
        map_key_scale(af_dict.get('tonal').get('key_scale'))
    )
    tmp_list.append(af_dict.get('tonal').get('key_strength'))

    # Add 36 values from tonal.hpcp.mean
    for hpcp in af_dict.get('tonal').get('hpcp').get('mean'):
        tmp_list.append(hpcp)

    # Add low level descriptors
    # Add 13 values from lowlevel.mfcc.mean
    for mfccmean in af_dict.get('lowlevel').get('mfcc').get('mean'):
        tmp_list.append(mfccmean)

    # Add 13 values from diagonal of lowlevel.mfcc.cov
    mfcc_cov = af_dict.get('lowlevel').get('mfcc').get('cov')
    for i in range(len(mfcc_cov)):
        tmp_list.append(mfcc_cov[i][i])

    # Add scalar low-level values
    tmp_list.append(af_dict.get('lowlevel').get('spectral_centroid').get('mean'))
    tmp_list.append(af_dict.get('lowlevel').get('spectral_rolloff').get('mean'))
    tmp_list.append(af_dict.get('lowlevel').get('spectral_flux').get('mean'))
    tmp_list.append(af_dict.get('lowlevel').get('zerocrossingrate').get('mean'))
    tmp_list.append(af_dict.get('lowlevel').get('zerocrossingrate').get('var'))

    # Add rhythmical scalar values
    tmp_list.append(af_dict.get('rhythm').get('bpm'))
    tmp_list.append(af_dict.get('rhythm').get('danceability'))
    tmp_list.append(af_dict.get('rhythm').get('beats_loudness').get('mean'))
    tmp_list.append(af_dict.get('rhythm').get('beats_loudness').get('var'))
    tmp_list.append(af_dict.get('rhythm').get('onset_rate'))

    d = len(tmp_list) # Dimension of the vector
    # Instantiate empty a Numpy array
    result = np.array(tmp_list, dtype='float32')
    # Transform array into a 1 x D
    result = result.reshape(1, d)

    # print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexVectorSchedl: Created a {result.shape} vector")
    return result

###### Executable ########
if __name__ == "__main__":
    load_dotenv()
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DATA_PATH = os.getenv("DATA_PATH")
    with open (f"{DATA_PATH}/miscellaneous/audio_features_sample.json", 'r') as f:
        af = json.load(f)
    vector = build_index_vector_schedl(af)
    print(vector)
