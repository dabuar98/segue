import logging
import os
import tempfile
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from dotenv import load_dotenv
from scripts.utils import is_valid_int
from api.models import *
from api.query_cache import get_query, set_query, delete_query, PENDING, READY, FAILED
from .serialisers import TrackSerialiser
import magic
import faiss
import numpy as np
from app.celery.tasks import compute_query

"""
To run it:
    1. curl -s -X POST http://localhost:8000/api/queries/ -F "track=@data/sample.mp3"     -> {"query_id": "<id>"}
    2. curl -s http://localhost:8000/api/queries/<id>/                                    -> wait for "ready"
    3. curl -s "http://localhost:8000/api/queries/<id>/similar/?n=10&subgenre=techno" | python -m json.tool
"""

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")

# Create logger to print any error to the console
logger = logging.getLogger(__name__)

# Load indices
faiss_index_schedl = faiss.read_index(f"{DATA_PATH}/indexes/index_schedl.faiss")
faiss_index_tzanetakis = faiss.read_index(f"{DATA_PATH}/indexes/index_tzanetakis.faiss")
faiss_index_bogdanov = faiss.read_index(f"{DATA_PATH}/indexes/index_bogdanov.faiss")

# Maps a descriptor set name to its faiss index
DESCRIPTOR_SETS = {
    'schedl': faiss_index_schedl,
    'tzanetakis': faiss_index_tzanetakis,
    'bogdanov': faiss_index_bogdanov,
}


@require_POST
@csrf_exempt
def create_query(request):
    """
    Receives an audio file and hands the computation of its query vector over to a Celery worker. The response is
    returned with the query_id to check the status and retrieve the similar tracks
    """
    try:
        # Retrieve the parameters passed on the request
        audio_file = request.FILES.get('track')
        if audio_file is None:
            return JsonResponse({'error': 'track is required'}, status=400)

        # Which descriptor set to compute similarity with (Default Schedl's)
        descriptor_set = request.POST.get('descriptor_set', 'schedl')

        # Validate that descriptor_set is a known descriptor set
        if descriptor_set not in DESCRIPTOR_SETS:
            return JsonResponse({'error': f"descriptor_set must be one of {list(DESCRIPTOR_SETS.keys())}"}, status=400)

        # Create temporary file to store submitted audio file
        suffix = os.path.splitext(audio_file.name)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            # Split the audio file in chunks to avoid overwhelming the system
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        # Validate if uploaded file is an audio file using magic number and MIME type
        if 'audio' not in magic.from_file(tmp_path, mime=True):
            os.remove(tmp_path)
            return JsonResponse({'error': 'only audio files are supported'}, status=400)

        query_id = str(uuid.uuid4())

        # Mark the query as pending before starting the task, so the worker can't finish before the entry exists
        set_query(query_id, PENDING, descriptor_set)

        try:
            # The worker removes the uploaded file once it is processed
            compute_query.delay(query_id, tmp_path, descriptor_set)
        except Exception:
            # The task never started (e.g. broker unreachable), so nothing else will clean up
            os.remove(tmp_path)
            delete_query(query_id)
            raise

        return JsonResponse({'query_id': query_id, 'status': PENDING}, status=202)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'error': 'system error'}, status=500)


@require_GET
def query_status(request, query_id):
    """
    Returns whether the query vector is still being computed, is ready, or failed
    """
    query = get_query(query_id)
    if query is None:
        return JsonResponse({'error': 'query not found or expired'}, status=404)

    return JsonResponse({
        'query_id': str(query_id),
        'status': query['status'],
        'descriptor_set': query['descriptor_set'],
    })


@require_GET
def similar(request, query_id):
    """
    Returns the tracks most similar to a previously computed query vector, applying the filters passed on the request
    """
    try:
        # Get number of tracks to return (Default 20)
        n = request.GET.get('n', 20)

        # Show similarity between query track and returned vector? (Default False)
        show_sim = request.GET.get('show_sim', 'false').lower()

        # Filter recommended tracks by subgenre (Default None, i.e. no filtering)
        subgenre = request.GET.get('subgenre', None)

        # Validate if n is an integer, return error otherwise
        if not is_valid_int(n): return JsonResponse({'error': 'n must be a integer'}, status=400)
        n = int(n)

        # Validate that n is a positive number
        if n < 0: return JsonResponse({'error': 'n must be a positive integer'}, status=400)

        # Limit the number of recommendations to max 50 to avoid memory overload
        if n > 50: return JsonResponse({'error': 'n must be less than 50'}, status=400)

        # Validate if dist is a boolean
        if show_sim not in ['true', 'false']:
            return JsonResponse({'error': 'dist must be a boolean'}, status=400)

        # Retrieve the query vector computed by the Celery worker
        query = get_query(query_id)
        if query is None:
            return JsonResponse({'error': 'query not found or expired'}, status=404)
        if query['status'] == PENDING:
            return JsonResponse({'error': 'query is still being processed'}, status=409)
        if query['status'] == FAILED:
            return JsonResponse({'error': 'audio feature extraction failed'}, status=422)

        # Resolve the faiss index for the descriptor set the vector was computed with
        faiss_index = DESCRIPTOR_SETS[query['descriptor_set']]

        # The cache returns the vector as a list, faiss needs a float32 numpy array
        query_vector = np.array(query['vector'], dtype=np.float32)

        # Normalise query vector
        faiss.normalize_L2(query_vector)

        # Store database objects retrieved in a dict
        tracks_objects = []
        tracks_distances = []

        # Store indices previously visited
        seen_indices = set()

        # Number of candidates to pull from the index this pass
        search_k = n
        max_k = faiss_index.ntotal

        while len(tracks_objects) < n:
            # Compute search
            distances, indices = faiss_index.search(query_vector, search_k)

            for index, distance in zip(indices[0], distances[0]):
                # Faiss pads the results with -1 when asking for more candidates than the index holds
                if index == -1:
                    break

                # Skip candidates already seen previously
                if index in seen_indices:
                    continue
                seen_indices.add(index)

                # Retrieve object from database
                track_obj = Tracks.objects.get(id=index)

                # If a subgenre filter is set, skip tracks whose subgenres don't match or contain it
                if subgenre and not track_obj.genres.filter(genre__icontains=subgenre).exists():
                    continue

                tracks_objects.append(track_obj)
                tracks_distances.append(distance)

                if len(tracks_objects) == n:
                    break

            # Stop once we've searched the entire index
            if search_k >= max_k:
                break

            # Double each pass to reach new candidates
            search_k = min(search_k * 2, max_k)

        serialiser = TrackSerialiser(tracks_objects, many=True)

        if show_sim == 'true':
            for track, distance in zip(serialiser.data, tracks_distances):
                track['similarity'] = round(float(distance), 6)

        return JsonResponse(serialiser.data, safe=False)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'error': 'system error'}, status=500)
