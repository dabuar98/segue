"""
Build a 1 x D vector where D is the dimension (231 descriptor values) that is passed as query vector to compute similarity
Parameters:
    input_path (str) : Path to the query track
Returns:
    result (nparray): A 1 x D Numpy array containing the values of the audio descriptors
"""
import numpy as np
from extract_query_descriptors import extract_query_descriptors
from datetime import datetime

def map_key(key):
    """
    Map key to its integer value (Representation of pitch class in set theory) [1]
    :params key: (str) : Keys in { "A", "Bb", "B", "C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab" } [2]
    :returns value: (int) : Value to be mapped
    References:
        [1] M. Lavengood, "Pitch and pitch class," in Open Music Theory, VIVA Pressbooks, 2023.
            [Online]. Available: https://viva.pressbooks.pub/openmusictheory/chapter/pitch-and-pitch-class/.
            [Accessed: Jul. 26, 2026].
        [2] Music Technology Group, Universitat Pompeu Fabra, "key.cpp," Essentia (source code repository), commit b9fa6cb, GitHub.
            [Online]. Available: https://github.com/MTG/essentia/blob/v2.1_beta5-1445-gb9fa6cb6/src/algorithms/tonal/key.cpp.
            [Accessed: Jul. 26, 2026].
    """
    key_map = {
        'C': 0,
        'C#': 1,
        'D': 2,
        'Eb': 3,
        'E': 4,
        'F': 5,
        'F#': 6,
        'G': 7,
        'Ab': 8,
        'A': 9,
        'Bb': 10,
        'B': 11,
    }

    return key_map[key]

def map_key_scale(key_scale):
    """
    :params key_scale: (str) : scale of the key (major or minor)
    :returns value: (int) : Value to be mapped (1 or 0)
    """
    return 1 if key_scale == 'major' else 0

def build_query_vector(input_path):
    # Compute audio descriptors
    descriptors = extract_query_descriptors(input_path)
    # Store descriptors in a list
    tmp_list = []

    # Add scalar tonal key values
    tmp_list.append(
        map_key(descriptors.get('tonal').get('key_edma').get('key'))
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

    # Add 169 values from lowlevel.mfcc.cov (13x13 covariance matrix flattened)
    for mfcccov_row in descriptors.get('lowlevel').get('mfcc').get('cov'):
        tmp_list.extend(mfcccov_row)

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
    result = np.array(tmp_list, dtype='float32')
    # Transform array into a 1 x D
    result = result.reshape(1, d)

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildQueryVector: Created a {result.shape} vector")
    return result