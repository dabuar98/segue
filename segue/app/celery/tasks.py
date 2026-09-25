import os
from celery import shared_task
from dotenv import load_dotenv
import joblib
from scripts.build_query_vector_bogdanov import build_query_vector_bogdanov
from scripts.build_query_vector_schedl import build_query_vector_schedl
from scripts.build_query_vector_tzanetakis import build_query_vector_tzanetakis

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")

# Load scalers
scaler_schedl = joblib.load(f"{DATA_PATH}/scalers/index_scaler_schedl.joblib")
scaler_tzanetakis = joblib.load(f"{DATA_PATH}/scalers/index_scaler_tzanetakis.joblib")
scaler_bogdanov = joblib.load(f"{DATA_PATH}/scalers/index_scaler_bogdanov.joblib")
pca = joblib.load(f"{DATA_PATH}/scalers/index_bogdanov_pca.joblib")

# Maps a descriptor set name to its (scaler, query vector builder) pair
DESCRIPTOR_SETS = {
    'schedl': (scaler_schedl, build_query_vector_schedl),
    'tzanetakis': (scaler_tzanetakis, build_query_vector_tzanetakis),
    'bogdanov': (scaler_bogdanov, build_query_vector_bogdanov),
}

# To start celery workers (run from the project root): celery -A app worker --loglevel=info

# The task of extracting audio descriptors is handed over to a Celery worker to offload computation from main thread
@shared_task
def extract_audio_features(track, descriptor_set):
    '''
    This function extracts audio features from an audio file
    Args:
        track: the audio file
        descriptor_set: The descriptor set to be used to extract audio features
    Returns:
        vector (1xN list, since Celery results must be JSON serialisable)

    '''
    scaler, build_query_vector_fn = DESCRIPTOR_SETS[descriptor_set]
    # Compute audio features
    vector = build_query_vector_fn(track)
    # Apply scaler
    vector = scaler.transform(vector)

    if descriptor_set == 'bogdanov':
        # Apply PCA to query vector
        vector = pca.transform(vector)

    return vector.tolist()
