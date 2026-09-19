import json
import os
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from .utils import map_key_former_version, map_key_scale

def build_index_vector_tzanetakis(af_dict):
    """
    Create an 1 xD array with the audio features values retrieved for a mbid.
    The selection of the audio features are based on Tzanetakis's thesis [1]
    Args:
        af_dict (dict): A dict representation of the audio features

    Returns:
        result (nparray): A 1 x D Numpy array containing the values of the audio descriptors

    References:
        [1]     G. Tzanetakis, Manipulation, Analysis and Retrieval Systems for Audio Signals. PhD thesis,
                2002.
    """
    # Timbre - Sound texture: Mean over the whole file of texture Short Time Fourier Transform  (STFT)-based features
    # 8 dimensions as low energy is not computed by Essentia and cannot be derived from any other descriptor
    tmp_list = [af_dict.get('lowlevel').get('spectral_centroid').get('mean'),
                af_dict.get('lowlevel').get('spectral_centroid').get('var'),
                af_dict.get('lowlevel').get('spectral_rolloff').get('mean'),
                af_dict.get('lowlevel').get('spectral_rolloff').get('var'),
                af_dict.get('lowlevel').get('spectral_flux').get('mean'),
                af_dict.get('lowlevel').get('spectral_flux').get('var'),
                af_dict.get('lowlevel').get('zerocrossingrate').get('mean'),
                af_dict.get('lowlevel').get('zerocrossingrate').get('var')]

    # Timbre - Sound texture: Means over the whole file of texture MFCCs
    # Means and variances of the first five MFCCs coefficient (10 dimensions)
    mfcc_mean = af_dict.get('lowlevel').get('mfcc').get('mean')
    mfcc_cov = af_dict.get('lowlevel').get('mfcc').get('cov')
    for i in range(1, 6):
        # Do not include DC term (The first coefficient)
        tmp_list.append(mfcc_mean[i])
    for i in range (1, 6):
        tmp_list.append(mfcc_cov[i][i])

    # Beat content - Rhythm: Features based on beat histograms (6 dimensions)
    # Mean of first and second histograms peaks with their weights and spreads
    for descriptor in [
        'bpm_histogram_first_peak_bpm',
        'bpm_histogram_first_peak_weight',
        'bpm_histogram_first_peak_spread',
        'bpm_histogram_second_peak_bpm',
        'bpm_histogram_second_peak_weight',
        'bpm_histogram_second_peak_spread',
    ]:
        tmp_list.append(af_dict.get('rhythm').get(descriptor).get('mean'))

    # Pitch content - Harmony: Features based on pitch histograms (4 dimensions)
    # The most dominant pitch class of the song
    tmp_list.append(
        map_key_former_version(af_dict.get('tonal').get('chords_key'))
    )
    # The most dominant octave range of the dominant musical key
    tmp_list.append(
        map_key_scale(af_dict.get('tonal').get('chords_scale'))
    )

    # Strength of the pitch detection (instead of using pitch histogram, Essentia uses chord histogram)
    tmp_list.append(af_dict.get('tonal').get('chords_strength').get('mean'))
    tmp_list.append(af_dict.get('tonal').get('chords_strength').get('var'))

    d = len(tmp_list) # Dimension of the vector
    # Instantiate empty a Numpy array
    result = np.array(tmp_list, dtype='float32')
    # Transform array into a 1 x D
    result = result.reshape(1, d)

    # print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexVectorTzanetakis: Created a {result.shape} vector")
    return result

###### Executable ########
if __name__ == "__main__":
    load_dotenv()
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DATA_PATH = os.getenv("DATA_PATH")
    with open (f"{DATA_PATH}/miscellaneous/audio_features_sample.json", 'r') as f:
        af = json.load(f)
    vector = build_index_vector_tzanetakis(af)
    print(vector)
