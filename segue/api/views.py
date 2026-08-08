import json
import os
import tempfile
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from dotenv import load_dotenv
from scripts.compute_similarity import compute_similarity

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

    # Traverse both arrays at the same time (both have the same dimension)
    for distance, index in zip(distances[0], indices[0]):
        result.append({
            'mbid': list(tracks.keys())[index],
            'title': list(tracks.values())[index]['title'],
            'artist': list(tracks.values())[index]['artist'],
            'album': list(tracks.values())[index]['album'],
            'subgenres': list(tracks.values())[index]['subgenres'],
            'date': list(tracks.values())[index]['date'],
            'distance': float(distance),
        })
    return JsonResponse(result, safe=False)
