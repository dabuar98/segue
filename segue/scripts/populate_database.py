"""
populate_database traverse a list with track info and builds the tables Tracks and Subgenres
based on models

Parameters:
    tracks (JSON): Resulting file from running get_tracks
Returns:
    None
"""
import os
import sys
import django
from pathlib import Path
from django.db import transaction
import json
from dotenv import load_dotenv
from datetime import datetime

# Inject .env values to os.environ
load_dotenv()

# Path to data
DATA_PATH = os.getenv("DATA_PATH")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from app.models import *

def populate_database(tracks):
    # Remove previous objects
    TrackSubgenreLink.objects.all().delete()
    Subgenres.objects.all().delete()
    Tracks.objects.all().delete()
    processed = 0

    # Read JSON file
    with open(tracks) as f:
        tracks = json.load(f)
    
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] PopulateDatabase: Building Database")
    with transaction.atomic():
        # Bulk insert all tracks in one query
        tracks_created = Tracks.objects.bulk_create([
            Tracks(
                mbid=mbid,
                title=(metadata.get('title') or [''])[0], # Extract data inside the list
                artist=(metadata.get('artist') or [''])[0],
                album=(metadata.get('album') or [''])[0],
                date=(metadata.get('date') or [''])[0],
            )
            for mbid, metadata in tracks.items()
       ])

        # Collect unique (mbid, genre) pairs and bulk insert subgenres
        subgenre_pairs = {
            (mbid, genre)
            for mbid, metadata in tracks.items()
            for genre in metadata.get('subgenres', 'No subgenres')
        }

        subgenres_created = Subgenres.objects.bulk_create([
            Subgenres(mbid=mbid, genre=genre)
            for mbid, genre in subgenre_pairs
       ])

        # Populate junction table
        # Link each track only to its own subgenres
        tracks_by_mbid = {track.mbid: track for track in tracks_created}
        subgenres_by_key = {(subgenre.mbid, subgenre.genre): subgenre for subgenre in subgenres_created}

        TrackSubgenreLink.objects.bulk_create([
            TrackSubgenreLink(
                track=tracks_by_mbid[mbid],
                subgenre=subgenres_by_key[(mbid, genre)]
            )
            for mbid, genre in subgenre_pairs
       ])

        processed += 1

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] PopulateDatabase: Populated {len(tracks_created):,} tracks")

# Populate database
tracks = f'{DATA_PATH}/tracks.json'
populate_database(tracks)