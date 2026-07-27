"""
Receive a dict containing track info and remove meaningless tracks i.e. tracks without title and artist
Parameters:
    tracks (dict): Dict resulting extract_metadata
Return:
    tracks (dict): Cleaned dict
"""
from datetime import datetime

def clean_tracks(tracks):
    result = {}
    for key, info in tracks.items():
        if info.get('title') is not None and info.get('artist') is not None:
            result[key] = info
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] CleanTracks: Removed {len(tracks) - len(result):,}/{len(tracks):,} tracks without title and artist")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] CleanTracks: Total tracks after cleaning: {len(result):,}")
    return result