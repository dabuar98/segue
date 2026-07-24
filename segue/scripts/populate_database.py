"""
populate_database traverse a list with track dicts and builds the tables Tracks and Subgenres
based on models

Parameters:
    tracklist (list): List containing track dicts with metadata
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
import csv

sys.path.append('/home/dabuar/Documents/Final-Project/dev/segue_music_recommender')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'segue.settings')
django.setup()

from django.db import transaction
from api.models import *
from add_metadata import add_metadata
from build_metadatas import build_metadatas
from extract_electronic_tracks_ids import extract_ids_electronic_genres

def populate_database(track_list):
    TrackSubgenreLink.objects.all().delete()
    Subgenres.objects.all().delete()
    Tracks.objects.all().delete()
    processed = 0
    
    print(f"[populate_database][INFO] - Building Database . . .")
    with transaction.atomic():
        # Bulk insert all tracks in one query
        Tracks.objects.bulk_create([
            Tracks(
                mb_id=track['mbid'],
                title=track.get('title', ''),
                artist=track.get('artist', ''),
                album=track.get('album', ''),
                date=track.get('date', ''),
            )
            for track in track_list
        ])

        # Collect unique (mbid, genre) pairs and bulk insert subgenres
        subgenre_pairs = {
            (track['mbid'], genre)
            for track in track_list
            for genre in track.get('subgenres', set())
        }
        Subgenres.objects.bulk_create(
            [Subgenres(mb_id=mbid, genre=genre) for mbid, genre in subgenre_pairs],
            ignore_conflicts=True,
        )

        # Fetch inserted rows to get their PKs for linking
        mbids = [track['mbid'] for track in track_list]
        track_lookup = {t.mb_id: t for t in Tracks.objects.filter(mb_id__in=mbids)}
        subgenre_lookup = {
            (s.mb_id, s.genre): s
            for s in Subgenres.objects.filter(mb_id__in=mbids)
        }

        # Bulk insert all junction-table rows in one query
        links = [
            TrackSubgenreLink(
                track=track_lookup[track['mbid']],
                subgenre=subgenre_lookup[(track['mbid'], genre)],
            )
            for track in track_list
            if track['mbid'] in track_lookup
            for genre in track.get('subgenres', set())
            if (track['mbid'], genre) in subgenre_lookup
        ]
        TrackSubgenreLink.objects.bulk_create(links)
        processed += 1

    print(f"[populate_database][INFO] - Populated {len(track_list):,} tracks")


#### Integration Test ######
metadata_path = '/home/dabuar/Documents/Final-Project/dev/audio_metadata'
audioft_path = '/home/dabuar/Documents/Final-Project/dev/audio_features'

ids = extract_ids_electronic_genres(metadata_path)
track_list = build_metadatas(ids, metadata_path)
track_list = add_metadata(track_list, audioft_path)
populate_database(track_list)