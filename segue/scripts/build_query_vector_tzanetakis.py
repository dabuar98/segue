import os
import numpy as np
from dotenv import load_dotenv
from .extract_query_descriptors import extract_query_descriptors
from .utils import map_key_current_version, map_key_scale
from datetime import datetime
def build_query_vector_tzanetakis(query_track):
    """
    Build a 1 x D vector where D is the dimension (number of descriptors) that is passed as query vector to compute
    similarity
    Args:
        query_track: Path to the query track (string)

    Returns:
        query_vector: 1 x D Numpy array containing the values of the audio descriptors

    """
    # Compute audio descriptors
    descriptors = extract_query_descriptors(query_track)

    # Timbre - Sound texture: Mean over the whole file of texture Short Time Fourier Transform  (STFT)-based features
    # 8 dimensions as low energy is not computed by Essentia and cannot be derived from any other descriptor
    tmp_list = [descriptors.get('lowlevel').get('spectral_centroid').get('mean'),
                descriptors.get('lowlevel').get('spectral_centroid').get('var'),
                descriptors.get('lowlevel').get('spectral_rolloff').get('mean'),
                descriptors.get('lowlevel').get('spectral_rolloff').get('var'),
                descriptors.get('lowlevel').get('spectral_flux').get('mean'),
                descriptors.get('lowlevel').get('spectral_flux').get('var'),
                descriptors.get('lowlevel').get('zerocrossingrate').get('mean'),
                descriptors.get('lowlevel').get('zerocrossingrate').get('var')]

    # Timbre - Sound texture: Means over the whole file of texture MFCCs
    # Means and variances of the first five MFCCs coefficient (10 dimensions)
    mfcc_mean = descriptors.get('lowlevel').get('mfcc').get('mean')
    mfcc_cov = descriptors.get('lowlevel').get('mfcc').get('cov')
    for i in range(1, 6):
        # Do not include DC term (The first coefficient)
        tmp_list.append(mfcc_mean[i])
    for i in range(1, 6):
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
        tmp_list.append(descriptors.get('rhythm').get(descriptor))

    # Pitch content - Harmony: Features based on pitch histograms (4 dimensions)
    # The most dominant pitch class of the song
    tmp_list.append(
        map_key_current_version(descriptors.get('tonal').get('chords_key'))
    )
    # The most dominant octave range of the dominant musical key
    tmp_list.append(
        map_key_scale(descriptors.get('tonal').get('chords_scale'))
    )

    # Strength of the pitch detection (instead of using pitch histogram, Essentia uses chord histogram)
    tmp_list.append(descriptors.get('tonal').get('chords_strength').get('mean'))
    tmp_list.append(descriptors.get('tonal').get('chords_strength').get('var'))


    d = len(tmp_list) # Dimension of the vector
    query_vector = np.array(tmp_list, dtype='float32')
    # Transform array into a 1 x D
    query_vector = query_vector.reshape(1, d)

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildQueryVector: Created a {query_vector.shape} vector")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexMatrix: {"There are values missing" if np.isnan(query_vector).any() else "There are not values missing"}")

    return query_vector

###### Executable ########
if __name__ == "__main__":
    load_dotenv()
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DATA_PATH = os.getenv("DATA_PATH")
    vector = build_query_vector_tzanetakis(f"{DATA_PATH}/miscellaneous/sample.mp3")
    print(vector)