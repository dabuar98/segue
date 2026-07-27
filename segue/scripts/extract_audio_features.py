'''
Extract the audio features from the zipped file that matches the mbid in the resulting dict from extract_subgenres.

Parameters:
    tracks (dict) : Resulting dict from extract_subgenres.
    input_path (string): String containing the path to the zipped file
    output_path (string): String containing the path to the extracted audio files

Returns:
    None
'''

import tarfile
import os
from pathlib import Path
from datetime import datetime

def extract_audio_features(tracks, input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)
    total_extracted = 0

    # Store all the IDs
    ids = list(tracks.keys())

    # Store the name of the .bz2 file
    candidate = [f for f in os.listdir(input_path) if f.endswith(".tar.bz2")]

    # Extract file with matching ID without unzipping it
    with tarfile.open(os.path.join(input_path, candidate[0]), "r:bz2") as tar:
        print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractAudioFeatures: Started extracting audio features")
        for member in tar:
            basename = os.path.basename(member.name)
            if basename.endswith(".json"):
                id = basename[:-5] # Get the track id without .json
                if id in ids:
                    file_obj = tar.extractfile(member)
                    if file_obj:
                        out_path = os.path.join(output_path, basename)
                        with open(out_path, "wb") as f:
                            f.write(file_obj.read())
                    total_extracted += 1

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractAudioFeatures: Extracted {total_extracted:,} files")