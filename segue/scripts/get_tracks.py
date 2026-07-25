"""
Run the pipeline from downloading the audio features to data cleaning. 
Create a JSON file containing track information
Parameters:
    None
Returns:
    None
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
from pathlib import Path

# Inject .env values to os.environ
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

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
        # Add metadata to tracks
        tracks = extract_metadata(tracks, audio_ft_path)
        # Upload audio features to s3
        # upload_to_s3(audio_ft_path)
        # Delete folder storing zipped audio features
        cleanup(audio_ft_zipped_path)
        # Delete folder storing JSON audio features
        cleanup(audio_ft_path)

    # Clean tracks
    tracks = clean_tracks(tracks)

    # Store result as a separate JSON file that other scripts can process
    with open(f"{BASE_DIR}/tracks.json", "w", encoding="utf-8") as file:
        json.dump(tracks, file, default=list)

if __name__ == "__main__":
    get_tracks()