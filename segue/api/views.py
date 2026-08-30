import json
import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from dotenv import load_dotenv
from scripts.compute_similarity import compute_similarity
from app.models import *
from .serialisers import TrackSerialiser
import magic

"""
To run it curl -s -X POST http://localhost:8000/api/similar/ -F "audio=@data/sample.mp3" | python -m json.tool
"""

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")

# Read JSON file
with open(f"{DATA_PATH}/tracks.json", "r") as f:
    tracks = json.loads(f.read())

@require_POST
@csrf_exempt
def similar(request):
    # Retrieve the parameters passed on the request
    audio_file = request.FILES['audio']

    # Get number of tracks to return (Default 20)
    n = request.POST.get('n', 20)

    # Show distance between query track and returned vector? (Default False)
    dist = request.POST.get('POST', 'false')

    # Show cosine-based similarity? (Default False)
    sim = request.POST.get('POST', 'false')

    # Validate if n is an integer, return error otherwise
    try:
        n = int(n)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'n must be an integer'}, status=400)

    # Validate if dist is a boolean
    if dist.lowercase() not in ['true', 'false']:
        return JsonResponse({'error': 'dist must be a boolean'}, status=400)

    # Validate if sim is a boolean
    if sim.lowercase() not in ['true', 'false']:
        return JsonResponse({'error': 'sim must be a boolean'}, status=400)

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

    try:
        distances, indices = compute_similarity(tmp_path, n)
    finally:
        os.remove(tmp_path)

    # Store database objects retrieved in a dict
    tracks_objects = []

    for index in indices[0]:
        # Get mbid from tracks using index
        mbid = list(tracks.keys())[index]
        # Retrieve object from database using mbid and add it to tracks_objects
        tracks_objects.append(Tracks.objects.get(mbid=mbid))

    serialiser = TrackSerialiser(tracks_objects, many=True)
    return JsonResponse(serialiser.data, safe=False)
