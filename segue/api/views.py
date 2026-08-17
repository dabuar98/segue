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
    result = []
    audio_file = request.FILES['audio']

    # Create temporary file to store submitted audio file
    suffix = os.path.splitext(audio_file.name)[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        for chunk in audio_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name
    try:
        distances, indices = compute_similarity(tmp_path)
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
