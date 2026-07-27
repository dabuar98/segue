"""
Extract the ids and subgenres of the tracks whose main genre is 'electronic' and its subgenres are derived from it
i.e. are in the form electronic---(subgenre) (According to Bogdanov et al. [1]) from the genre datasets.
It returns a dict mapping the track ID to its subgenres.
Parameters:
    input_path (string): A string representation of the path to the directory containing the genre datasets
Returns:
    dict: A dict mapping ID to subgenres
References:
    [1] Bogdanov, D., Porter A., Schreiber H., Urbano J., & Oramas S. (2019).
    The AcousticBrainz Genre Dataset: Multi-Source, Multi-Level, Multi-Label, and Large-Scale.
    20th International Society for Music Information Retrieval Conference (ISMIR 2019).
"""
import os
from collections import defaultdict
from pathlib import Path
import csv
from datetime import datetime

def extract_subgenres(input_path):
    # Parse string to os path
    input_path = Path(input_path)
    total_processed = 0 # Number of tracks processed (for stats)
    total_tracks = 0
    result = {}
    subgenres_global = set() # Store unique genres

    # Read the files
    for filename in os.listdir(input_path):
        if filename.endswith(".tsv"):
            with open(os.path.join(input_path, filename), newline="") as f:
                print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractSubgenres: Reading {filename}")
                # Transform each row into a dict for easy traversal
                # e.g {
                #       'recordingmbid': '6eafad9e-3e4e-4af7-ad2c-dba94cfedecf',
                #       'releasegroupmbid': 'fa7475c1-78a3-31e3-8b27-ca4fef89ba12',
                #       'genre1': 'electronic',
                #       'genre2': 'electronic---ambient'
                #     }
                reader = csv.DictReader(f, delimiter="\t") # Use tab delimiter for TSV files
                for row in reader:
                    total_tracks += 1
                    genres = []
                    subgenres_local = set()
                    # Read genres (upper bound is exclusive)
                    for i in range(1, len(row) - 1):
                        if row[f'genre{i}']:
                            genres.append(row[f'genre{i}'].lower().strip())

                    # Check if subgenres start with 'electronic'
                    if genres and all(g.startswith("electronic") for g in genres):
                        mbid = row['recordingmbid']
                        for genre in genres:
                            subgenres = genre.split("---")
                            for subgenre in subgenres:
                                if subgenre != 'electronic':
                                    subgenres_global.add(subgenre) # Add subgenre for stats
                                    subgenres_local.add(subgenre) # Add subgenre to set in the dict
                        if mbid in result:
                            result[mbid]['subgenres'] |= subgenres_local # Merge subgenres if seen before
                        else:
                            result[mbid] = {'subgenres': subgenres_local}
                    total_processed += 1

    # Compute informational stats
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractSubgenres: Total tracks: {total_tracks:,}")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractSubgenres: Electronic tracks: {len(result):,}")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractSubgenres: Electronic subgenres: {len(subgenres_global):,}")
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractSubgenres: Processed tracks: {total_processed:,}")

    return result

#if __name__ == "__main__":
#    tracks = extract_subgenres('/home/dabuar/Documents/Final-Project/dev/audio_metadata')
#    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractSubgenres: {tracks[1:5]}")
