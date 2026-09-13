import json
import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from dotenv import load_dotenv
from scripts.build_query_vector import build_query_vector
from scripts.build_query_vector_tzanetakis import build_query_vector_tzanetakis
from app.models import *
from .serialisers import TrackSerialiser
import magic
import faiss
import joblib
from scripts.utils import cosine_similarity

"""
To run it curl -s -X POST http://localhost:8000/api/similar/ -F "audio=@data/sample.mp3" | python -m json.tool
"""

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")

# Read JSON file
with open(f"{DATA_PATH}/tracks.json", "r") as f:
    tracks = json.loads(f.read())

# Load index
faiss_index = faiss.read_index(f"{DATA_PATH}/index.faiss")

# Load scaler
scaler = joblib.load(f"{DATA_PATH}/index_scaler.joblib")

@require_POST
@csrf_exempt
def similar(request):
    # Retrieve the parameters passed on the request
    audio_file = request.FILES['audio']

    # Get number of tracks to return (Default 20)
    n = request.POST.get('n', 20)

    # Show distance between query track and returned vector? (Default False)
    show_sim = request.POST.get('show_sim', 'false').lower()

    # Filter recommended tracks by subgenre (Default None, i.e. no filtering)
    subgenre = request.POST.get('subgenre', None)

    # Show cosine-based similarity? (Default False)
    # sim = request.POST.get('sim', 'false').lower()

    # Validate if n is an integer, return error otherwise
    try:
        n = int(n)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'n must be an integer'}, status=400)

    # Validate that n is a positive number
    if n < 0: return JsonResponse({'error': 'n must be a positive integer'}, status=400)

    # Limit the number of recommendations to max 50 to avoid memory overload
    if n > 50: return JsonResponse({'error': 'n must be less than 50'}, status=400)

    # Validate if dist is a boolean
    if show_sim not in ['true', 'false']:
        return JsonResponse({'error': 'dist must be a boolean'}, status=400)

    # # Validate if sim is a boolean
    # if sim not in ['true', 'false']:
    #     return JsonResponse({'error': 'sim must be a boolean'}, status=400)

    # Create temporary file to store submitted audio file
    suffix = os.path.splitext(audio_file.name)[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        # Split the audio file in chunks to avoid overwhelming the system
        for chunk in audio_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    # Validate if uploaded file is an audio file using magic number and MIME type
    if 'audio' not in magic.from_file(tmp_path, mime=True):
        return JsonResponse({'error': 'only audio files are supported'}, status=400)

    # Build query vector
    # query_vector = build_query_vector(tmp_path)
    query_vector = build_query_vector_tzanetakis(tmp_path)

    # Apply scaler to query vector
    query_vector = scaler.transform(query_vector)

    # Normalise query vector
    faiss.normalize_L2(query_vector)

    try:
        distances, indices = faiss_index.search(query_vector, n)
    except Exception as e:
        return JsonResponse({'error': 'an error creating the recommendation occurred'}, status=500)
    finally:
        os.remove(tmp_path)

    # Store database objects retrieved in a dict
    tracks_objects = []
    tracks_distances = []

    for index, distance in zip(indices[0], distances[0]):
        # Get mbid from tracks using index
        mbid = list(tracks.keys())[index]
        # Retrieve object from database using mbid
        track_obj = Tracks.objects.get(mbid=mbid)

        # If a subgenre filter is set, skip tracks whose subgenres don't match or contain it
        if subgenre and not track_obj.genres.filter(genre__icontains=subgenre).exists():
            continue

        tracks_objects.append(track_obj)
        tracks_distances.append(distance)

    serialiser = TrackSerialiser(tracks_objects, many=True)

    if show_sim == 'true':
        for track, distance in zip(serialiser.data, tracks_distances):
            track['distance'] = round(float(distance), 6)

    # if sim == 'true':
    #     for track, idx in zip(serialiser.data, indices[0]):
    #         # Retrieve response vector from FAISS index
    #         vect = faiss_index.reconstruct(int(idx))
    #         # Compute cosine similarity
    #         similarity = cosine_similarity(query_vector, vect)
    #         # Display similarity as percentage
    #         track['similarity'] = round(similarity, 6)

    return JsonResponse(serialiser.data, safe=False)
