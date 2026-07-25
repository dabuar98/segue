#!/bin/bash
# Download and extract the genre datasets

# Load and export all variables from the .env file
export $(xargs < ../.env)

## Download the datasets
#echo "[get_genre_datasets][INFO] - Downloading discogs dataset"
#wget -q https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-discogs-train.tsv.bz2?download=1 -O "${GENRE_DATASET_PATH}/discogs-train.tsv.bz2"
#echo "[get_genre_datasets][INFO] - Downloading lastfm dataset"
#wget -q https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-lastfm-train.tsv.bz2?download=1 -O "${GENRE_DATASET_PATH}/lastfm-train.tsv.bz2"
#echo "[get_genre_datasets][INFO] - Downloading tagtraum dataset"
#wget -q https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-tagtraum-train.tsv.bz2?download=1 -O "${GENRE_DATASET_PATH}/tagtraum-train.tsv.bz2"

# Extract files
echo "[get_genre_datasets][INFO] - Extracting files"
bunzip2 "${GENRE_DATASET_PATH}/discogs-train.tsv.bz2"
bunzip2 "${GENRE_DATASET_PATH}/lastfm-train.tsv.bz2"
bunzip2 "${GENRE_DATASET_PATH}/tagtraum-train.tsv.bz2"

echo "[get_genre_datasets][INFO] - Done"

