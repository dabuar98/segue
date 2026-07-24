#!/bin/bash
# Download and extract the genre datasets

# Download the datasets
echo "Downloading discogs dataset"
wget -q https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-discogs-train.tsv.bz2?download=1 -O discogs-train.tsv.bz2
echo "Downloading lastfm dataset"
wget -q https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-lastfm-train.tsv.bz2?download=1 -O lastfm-train.tsv.bz2
echo "Downloading tagtraum dataset"
wget -q https://zenodo.org/records/2553414/files/acousticbrainz-mediaeval-tagtraum-train.tsv.bz2?download=1 -O tagtraum-train.tsv.bz2

# Extract files
echo "Extracting files"
bunzip2 *.bz2

echo "Done"

