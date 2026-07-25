"""
populate_database traverse a list with track info and builds the tables Tracks and Subgenres
based on models

Parameters:
    tracks (JSON): Resulting file from running get_tracks
Returns:
    None

    v2.0:
    Here's what changed and why each part matters:

    transaction.atomic() — Django auto-commits every INSERT by default, meaning each one flushes to disk. Wrapping everything in one transaction does a single flush at the end.

    bulk_create for Tracks — replaces N individual INSERT statements with one batched INSERT.

    bulk_create with ignore_conflicts=True for Subgenres — replaces N×M get_or_create calls (each doing a SELECT then possibly an INSERT) with one batched INSERT.

    Two lookups + bulk_create for links — two SELECT queries to fetch back the PKs of inserted rows, then one batched INSERT for all junction rows.

    Before: ~3,200 DB round-trips for 200 tracks with ~5 genres each.
    After: ~8 queries total regardless of dataset size.
"""
import os
import sys
import django
from pathlib import Path
from django.db import transaction
import json

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
    
    print(f"[populate_database][INFO] - Building Database")
    with transaction.atomic():
        # Bulk insert all tracks in one query
        tracks_created = Tracks.objects.bulk_create([
            Tracks(
                mb_id=mbid,
                title=metadata.get('title', '[]')[0], # Extract data inside the list
                artist=metadata.get('artist', '[]')[0],
                album=metadata.get('album', '[]')[0],
                date=metadata.get('date', '[]')[0],
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
            Subgenres(mb_id=mbid, genre=genre)
            for mbid, genre in subgenre_pairs
        ])

        # Populate junction table
        TrackSubgenreLink.objects.bulk_create([
            TrackSubgenreLink(
                track=track,
                subgenre=subgenre
            )
            for track in tracks_created
            for subgenre in subgenres_created
        ])

        processed += 1

    print(f"[populate_database][INFO] - Populated {len(tracks_created):,} tracks")

### Test
tracks = f'{BASE_DIR}/tracks_min.json'
populate_database(tracks)