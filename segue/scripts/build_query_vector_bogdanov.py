import os
import numpy as np
from dotenv import load_dotenv
from .extract_query_descriptors import extract_query_descriptors
from datetime import datetime

def build_query_vector_bogdanov(query_track):
    """
    Build a 1 x D vector where D is the dimension (number of descriptors) that is passed as query vector to compute
    similarity. Mirrors build_index_vector_bogdanov's descriptor selection, computed live from a query audio file.
    Args:
        query_track: Path to the query track (string)

    Returns:
        query_vector: 1 x D Numpy array containing the values of the audio descriptors

    References:
        [1]     Bogdanov, D. (2013). From music similarity to music recommendation: computational approaches
                based on audio features and metadata (Doctoral dissertation). Universitat Pompeu Fabra.
                https://hdl.handle.net/10803/123776
    """
    # Compute audio descriptors
    descriptors = extract_query_descriptors(query_track)

    lowlevel = descriptors.get('lowlevel')
    rhythm = descriptors.get('rhythm')
    tonal = descriptors.get('tonal')

    # Timbral features
    # Bark bands: full band-energy mean array (27 dimensions)
    tmp_list = list(lowlevel.get('barkbands').get('mean'))

    # Pitch: substitute pitch_salience, as a generic pitch descriptor is not computed by this Essentia build.
    # Mean and variance (2 dimensions)
    tmp_list.append(lowlevel.get('pitch_salience').get('mean'))
    tmp_list.append(lowlevel.get('pitch_salience').get('var'))

    # MFCCs: mean coefficient array (13 dimensions)
    tmp_list.extend(lowlevel.get('mfcc').get('mean'))

    # MFCCs: diagonal of the covariance matrix (13 dimensions)
    mfcc_cov = lowlevel.get('mfcc').get('cov')
    for i in range(len(mfcc_cov)):
        tmp_list.append(mfcc_cov[i][i])

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

    # Spectral crest, flatness: mean and variance of each (4 dimensions)
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

    #  Rhythmic
    # BPM histogram first and second peaks: BPM, weight and spread of each (6 dimensions)
    for peak in ['first', 'second']:
        tmp_list.append(rhythm.get(f'bpm_histogram_{peak}_peak_bpm'))
        tmp_list.append(rhythm.get(f'bpm_histogram_{peak}_peak_weight'))
        tmp_list.append(rhythm.get(f'bpm_histogram_{peak}_peak_spread'))

    # Beats loudness: mean and variance (2 dimensions)
    tmp_list.append(rhythm.get('beats_loudness').get('mean'))
    tmp_list.append(rhythm.get('beats_loudness').get('var'))

    # Beats loudness bass: substitute the lowest-frequency band (index 0) of beats_loudness_band_ratio, as a
    # dedicated bass descriptor is not computed by this Essentia build. Mean and variance (2 dimensions)
    tmp_list.append(rhythm.get('beats_loudness_band_ratio').get('mean')[0])
    tmp_list.append(rhythm.get('beats_loudness_band_ratio').get('var')[0])

    #  Tonal
    # Untransposed harmonic pitch class profile (36 dimensions)
    tmp_list.extend(tonal.get('hpcp').get('mean'))

    # Transposed harmonic pitch class profile (36 dimensions)
    tmp_list.extend(tonal.get('thpcp'))

    # Key strength (1 dimension)
    tmp_list.append(tonal.get('key_edma').get('strength'))

    # Tuning frequency (1 dimension)
    tmp_list.append(tonal.get('tuning_frequency'))

    # Dissonance: mean and variance (2 dimensions)
    tmp_list.append(lowlevel.get('dissonance').get('mean'))
    tmp_list.append(lowlevel.get('dissonance').get('var'))

    # Chord change rate (1 dimension)
    tmp_list.append(tonal.get('chords_changes_rate'))

    # Chords histogram (24 dimensions)
    tmp_list.extend(tonal.get('chords_histogram'))

    # Chords strength: mean and variance (2 dimensions)
    tmp_list.append(tonal.get('chords_strength').get('mean'))
    tmp_list.append(tonal.get('chords_strength').get('var'))

    # Tuning equal tempered deviation (1 dimension)
    tmp_list.append(tonal.get('tuning_equal_tempered_deviation'))

    # Tuning non-tempered energy ratio (1 dimension)
    tmp_list.append(tonal.get('tuning_nontempered_energy_ratio'))

    # Tuning diatonic strength (1 dimension)
    tmp_list.append(tonal.get('tuning_diatonic_strength'))

    #  Miscellaneous
    # Average loudness (1 dimension)
    tmp_list.append(lowlevel.get('average_loudness'))

    # Zero-crossing rate: mean and variance (2 dimensions)
    tmp_list.append(lowlevel.get('zerocrossingrate').get('mean'))
    tmp_list.append(lowlevel.get('zerocrossingrate').get('var'))

    # Silence rate at the 20dB, 30dB and 60dB thresholds (3 dimensions)
    for threshold in ['20dB', '30dB', '60dB']:
        tmp_list.append(lowlevel.get(f'silence_rate_{threshold}').get('mean'))

    # Spectral RMS variance (1 dimension)
    tmp_list.append(lowlevel.get('spectral_rms').get('var'))

    d = len(tmp_list) # Dimension of the vector
    query_vector = np.array(tmp_list, dtype='float32')
    # Transform array into a 1 x D
    query_vector = query_vector.reshape(1, d)

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildQueryVectorBogdanov: Created a {query_vector.shape} vector")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] BuildQueryVectorBogdanov: {"There are values missing" if np.isnan(query_vector).any() else "There are not values missing"}")

    return query_vector

###### Executable ########
if __name__ == "__main__":
    load_dotenv()
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DATA_PATH = os.getenv("DATA_PATH")
    vector = build_query_vector_bogdanov(f"{DATA_PATH}/miscellaneous/sample.mp3")
    print(vector)
