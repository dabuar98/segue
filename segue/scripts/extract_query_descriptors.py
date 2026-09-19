import json
import os
import essentia.standard as es
from datetime import datetime
from dotenv import load_dotenv

def extract_query_descriptors(input_path):
    """
    Compute the audio features of the query track. The output of this script is used to build the query vector
    Args:
        input_path: Path to the query track (string)

    Returns:
        result: A dictionary containing the audio features of the query track (dictionary)
    """
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractQueryDescriptors: Extracting audio features")
    features, _ = es.MusicExtractor()(input_path)
    result = {}
    # Traverse audio features Pool
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractQueryDescriptors: Building result object")
    for key in features.descriptorNames():
        value = features[key]

        # Convert values to regular Python list (if applicable)
        try:
            value = value.tolist()
        except AttributeError:
            pass

        # Traverse the array of descriptors, without including the furthest one
        parts = key.split(".")
        d = result
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value

    # Work around to include bpm_histogram_first_peak_spread (Not included in 2.1-beta6-dev)
    print(
        f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractQueryDescriptors: Patching bpm_histogram first-peak fields")

    # Load file
    audio = es.MonoLoader(filename=input_path)()
    # Compute tempo beat intervals separately
    _, _, _, _, beats_intervals = es.RhythmExtractor2013()(audio)
    # Compute histogram statistics
    peak1_bpm, peak1_weight, peak1_spread, peak2_bpm, peak2_weight, peak2_spread, histogram = es.BpmHistogramDescriptors()(beats_intervals)

    # Add to the output
    result.setdefault("rhythm", {})
    result["rhythm"]["bpm_histogram_first_peak_weight"] = peak1_weight
    result["rhythm"]["bpm_histogram_first_peak_spread"] = peak1_spread

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractQueryDescriptors: Done")
    return result

###### Executable ########
if __name__ == "__main__":
    load_dotenv()
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DATA_PATH = os.getenv("DATA_PATH")
    descriptors = extract_query_descriptors(f"{DATA_PATH}/miscellaneous/sample.mp3")
    with open(f"{DATA_PATH}/miscellaneous/sample_query_descriptors.json", "w") as outfile:
        json.dump(descriptors, outfile)