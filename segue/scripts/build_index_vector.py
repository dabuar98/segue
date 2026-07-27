"""
Create an array D x 1 with the audio features values retrieved for a mbid
Parameters:
    af_dict (dict): A dict representation of the audio features
Returns:
    result (nparray): A 1 x D Numpy array containing the values of the audio descriptors
"""
import json
import numpy as np

def map_key(key):
    """
    Map key to its integer value (Representation of pitch class in set theory) [1]
    :params key: (str) : Keys in { "A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#" } [2]
    :returns value: (int) : Value to be mapped
    References:
    [1] M. Lavengood, "Pitch and pitch class," in Open Music Theory, VIVA Pressbooks, 2023.
        [Online]. Available: https://viva.pressbooks.pub/openmusictheory/chapter/pitch-and-pitch-class/.
        [Accessed: Jul. 26, 2026].
    [2] Music Technology Group, Universitat Pompeu Fabra, "key.cpp," essentia, v2.1_beta2.
        [Online]. Available: https://github.com/MTG/essentia/blob/v2.1_beta2/src/algorithms/tonal/key.cpp.
        [Accessed: Jul. 26, 2026].
    """
    # Key map with enharmonic equivalents A#/Bb, D#/Eb and G#/Ab from Essentia v2.1-beta2
    key_map = {
        'C': 0,
        'C#': 1,
        'D': 2,
        'D#': 3,
        'E': 4,
        'F': 5,
        'F#': 6,
        'G': 7,
        'G#': 8,
        'A': 9,
        'A#': 10,
        'B': 11,
    }

    return key_map[key]

def map_key_scale(key_scale):
    """
    :params key_scale: (str) : scale of the key (major or minor)
    :returns value: (int) : Value to be mapped (1 or 0)
    """
    return 1 if key_scale == 'major' else 0

def build_index_vector(af_dict):
    # Store descriptors in a list
    tmp_list = []

    # Add scalar tonal key values (former version)
    tmp_list.append(
        map_key(af_dict.get('tonal').get('key_key'))
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

    # Add 169 values from lowlevel.mfcc.cov (13x13 covariance matrix flattened)
    for mfcccov_row in af_dict.get('lowlevel').get('mfcc').get('cov'):
        tmp_list.extend(mfcccov_row)

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

    print(f"[build_index_vector][INFO] - Created a {result.shape} vector")
    return result