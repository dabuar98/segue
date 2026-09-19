import json
import os
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

def build_index_vector_bogdanov(af_dict):
    """
    Create an 1 xD array with the audio features values retrieved for a mbid.
    The selection of the audio features are restricted to a subset of the descriptor set proposed by
    Bogdanov [1]: bark bands, pitch, spectral centroid, spread, kurtosis, rolloff, decrease, skewness,
    high-frequency content, spectral complexity, spectral crest, flatness, flux, spectral energy, energy bands,
    strong peak, beats loudness, beats loudness bass, untransposed harmonic pitch class profile, key strength,
    average loudness, and zero-crossing rate.
    Args:
        af_dict (dict): A dict representation of the audio features

    Returns:
        result (nparray): A 1 x D Numpy array containing the values of the audio descriptors

    References:
        [1]     Bogdanov, D. (2013). From music similarity to music recommendation: computational approaches
                based on audio features and metadata (Doctoral dissertation). Universitat Pompeu Fabra.
                https://hdl.handle.net/10803/123776
    """
    lowlevel = af_dict.get('lowlevel')
    rhythm = af_dict.get('rhythm')
    tonal = af_dict.get('tonal')

    # Timbral features
    # Bark bands: full band-energy mean array (27 dimensions)
    tmp_list = list(lowlevel.get('barkbands').get('mean'))

    # Pitch: Mean and variance (2 dimensions)
    tmp_list.append(lowlevel.get('pitch_salience').get('mean'))
    tmp_list.append(lowlevel.get('pitch_salience').get('var'))

    # Spectral centroid, spread, kurtosis, rolloff, decrease, skewness: mean and variance of each (12 dimensions)
    for descriptor in [
        'spectral_centroid',
        'spectral_spread',
        'spectral_kurtosis',
        'spectral_rolloff',
        'spectral_decrease',
        'spectral_skewness',
    ]:
        tmp_list.append(lowlevel.get(descriptor).get('mean'))
        tmp_list.append(lowlevel.get(descriptor).get('var'))

    # High-frequency content: mean and variance (2 dimensions)
    tmp_list.append(lowlevel.get('hfc').get('mean'))
    tmp_list.append(lowlevel.get('hfc').get('var'))

    # Spectral complexity: mean and variance (2 dimensions)
    tmp_list.append(lowlevel.get('spectral_complexity').get('mean'))
    tmp_list.append(lowlevel.get('spectral_complexity').get('var'))

    # Spectral crest, flatness: Mean and variance of each (4 dimensions)
    tmp_list.append(lowlevel.get('barkbands_crest').get('mean'))
    tmp_list.append(lowlevel.get('barkbands_crest').get('var'))
    tmp_list.append(lowlevel.get('barkbands_flatness_db').get('mean'))
    tmp_list.append(lowlevel.get('barkbands_flatness_db').get('var'))

    # Spectral flux: mean and variance (2 dimensions)
    tmp_list.append(lowlevel.get('spectral_flux').get('mean'))
    tmp_list.append(lowlevel.get('spectral_flux').get('var'))

    # Spectral energy, energy bands, strong peak: mean and variance of each (12 dimensions)
    for descriptor in [
        'spectral_energy',
        'spectral_energyband_low',
        'spectral_energyband_middle_low',
        'spectral_energyband_middle_high',
        'spectral_energyband_high',
        'spectral_strongpeak',
    ]:
        tmp_list.append(lowlevel.get(descriptor).get('mean'))
        tmp_list.append(lowlevel.get(descriptor).get('var'))

    # Rhythmic features
    # Beats loudness: mean and variance (2 dimensions)
    tmp_list.append(rhythm.get('beats_loudness').get('mean'))
    tmp_list.append(rhythm.get('beats_loudness').get('var'))

    # Beats loudness bass: Mean and variance (2 dimensions)
    tmp_list.append(rhythm.get('beats_loudness_band_ratio').get('mean')[0])
    tmp_list.append(rhythm.get('beats_loudness_band_ratio').get('var')[0])

    # Tonal features
    # Untransposed harmonic pitch class profile (36 dimensions)
    tmp_list.extend(tonal.get('hpcp').get('mean'))

    # Key strength (1 dimension)
    tmp_list.append(tonal.get('key_strength'))

    # Miscellaneous
    # Average loudness (1 dimension)
    tmp_list.append(lowlevel.get('average_loudness'))

    # Zero-crossing rate: mean and variance (2 dimensions)
    tmp_list.append(lowlevel.get('zerocrossingrate').get('mean'))
    tmp_list.append(lowlevel.get('zerocrossingrate').get('var'))

    d = len(tmp_list) # Dimension of the vector
    # Instantiate empty a Numpy array
    result = np.array(tmp_list, dtype='float32')
    # Transform array into a 1 x D
    result = result.reshape(1, d)

    # print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildIndexVectorBogdanov: Created a {result.shape} vector")
    return result

###### Executable ########
if __name__ == "__main__":
    load_dotenv()
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DATA_PATH = os.getenv("DATA_PATH")
    with open (f"{DATA_PATH}/audio_features_sample.json", 'r') as f:
        af = json.load(f)
    vector = build_index_vector_bogdanov(af)
    print(vector)
