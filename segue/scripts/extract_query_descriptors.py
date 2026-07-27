'''
Compute the audio features of the query track. The output of this script is used to build the query vector
Parameters:
    input_path (str) : Path to the query track
Returns:
    result (dict) : A dictionary containing the audio features of the query track
'''

import essentia.standard as es
from datetime import datetime

def extract_query_descriptors(input_path):
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

    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] ExtractQueryDescriptors: Done")
    return result