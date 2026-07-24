"""
Run the pipeline from downloading the audio features to data cleaning.
Parameters:
    None
Returns:
    tracks (dict): A dictionary mapping ID to track information (title, artist, album, date and subgenres)
"""

from extract_subgenres import *
from extract_audio_features import *
from extract_metadata import *
from upload_to_s3 import *
from clean_tracks import *
import subprocess
import os
import json
from download_url import *
from dotenv import load_dotenv

# Inject .env values to os.environ
load_dotenv()

def cleanup(dir_path):
    print(f"[cleanup][INFO] - Removing {dir_path}")
    subprocess.run(["rm", "-r", dir_path], check=True)

def get_tracks():
    # Define where to locate data
    genre_dataset_path = os.getenv("GENRE_DATASET_PATH")
    audio_ft_path = os.getenv("AUDIO_FEATURES_PATH_TO_UNZIP")
    audio_ft_zipped_path = os.getenv("AUDIO_FEATURES_PATH_ZIP")

    pair_link = {
        '01': 'https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-features--train-01.tar.bz2?download=1',
        '23': 'https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-features-train-23.tar.bz2?download=1',
        '45': 'https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-features-train-45.tar.bz2?download=1',
        '67': 'https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-features-train-67.tar.bz2?download=1',
        '89': 'https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-features-train-89.tar.bz2?download=1',
        'ab': 'https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-features-train-ab.tar.bz2?download=1',
        'cd': 'https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-features-train-cd.tar.bz2?download=1',
        'ef': 'https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-features-train-ef.tar.bz2?download=1'
    }

    # Extract the ids and subgenres
    tracks = extract_subgenres(genre_dataset_path)

    for pair, url in pair_link.items():
        # Create directories to prevent errors after cleanup
        os.makedirs(audio_ft_path, exist_ok=True)
        os.makedirs(audio_ft_zipped_path, exist_ok=True)
        print(f"[get_tracks][INFO] - Created directories for audio features extraction for pair {pair}")
        # Download audio features
        zipped_file_path = os.path.join(audio_ft_zipped_path, f"train-{pair}.tar.bz2")
        download_url(url, zipped_file_path)
        # Extract audio features
        extract_audio_features(tracks, audio_ft_zipped_path, audio_ft_path)
        # Extract metadata
        extract_metadata(tracks, audio_ft_path)
        # Upload audio features to s3
        upload_to_s3(audio_ft_path)
        # Delete folder storing zipped audio features
        cleanup(audio_ft_zipped_path)
        # Delete folder storing JSON audio features
        cleanup(audio_ft_path)

    # Clean tracks
    clean_tracks(tracks)

    # Print tracks as JSON so it can be captured from the log file
    print(json.dumps(tracks, default=list, indent=2))
    return tracks

if __name__ == "__main__":
    get_tracks()