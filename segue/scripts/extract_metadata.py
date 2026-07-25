"""
Add to the dict resulting from extract_subgenres the track name, artist, album, and release date
Parameters:
    - tracks (dict): Dict resulting extract_subgenres
    - input_path (string): String representing the path of directory containing the extracted audio features
Returns:
    - tracks (dict): Dict resulting extract_subgenres with metadata added
"""
import os
from pathlib import Path
import json

def extract_metadata(tracks, input_path):
    input_path = Path(input_path)
    total_processed = 0
    # Copy tracks (and each track's dict) so the input is left untouched
    result = {id: dict(info) for id, info in tracks.items()}

    # Extract the metadata from the JSON files
    for file in os.listdir(input_path):
        if file.endswith(".json"):
            id = file[:-5]
            try:
                with open(os.path.join(input_path, file)) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                print(f"[extract_metadata][ERROR] - Error processing {id}")
                continue

            tags = data.get("metadata", {}).get("tags", {})
            # Add metadata
            result[id]['title'] = tags.get("title", None)
            result[id]['artist'] = tags.get("artist") if tags.get("artist") else tags.get("albumartist", None)
            result[id]['album'] = tags.get("album", None)
            result[id]['date'] = tags.get("date", None)

            total_processed += 1

    # Print stats
    print(f"[extract_metadata][INFO] - Processed {total_processed:,} tracks")
    return result
