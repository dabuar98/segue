"""
Unit tests for build_index_vector_bogdanov
Run it from the project directory with py -m unittest -v scripts.tests.test_build_vectors_bogdanov
"""
import json
import os
import sys
import unittest

import numpy as np
from dotenv import load_dotenv

# Import /scripts to sys path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build_index_vector_bogdanov import build_index_vector_bogdanov

# Add environment variables
load_dotenv()

DATA_PATH = os.getenv("DATA_PATH")

class TestBuildVectorsBogdanov(unittest.TestCase):
    def test_build_index_vector_bogdanov(self):
        with open(f"{DATA_PATH}/audio_features_sample.json") as f:
            data = json.load(f) # Transform to a Python dict

        result = build_index_vector_bogdanov(data) # Receives a Python dict
        # Test dimension: bark bands (27) + pitch (2) + spectral centroid/spread/kurtosis/rolloff/decrease/
        # skewness (12) + HFC (2) + spectral complexity (2) + crest/flatness (4) + flux (2) + spectral energy/
        # energy bands/strong peak (12) + beats loudness (2) + beats loudness bass (2) + untransposed HPCP (36)
        # + key strength (1) + average loudness (1) + zero-crossing rate (2) = 107
        self.assertEqual(result.shape, (1, 107))
        # Script should return a np array of type float32
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.dtype, np.float32)
        # No elements should be left unpopulated
        self.assertFalse(np.isnan(result).any())

if __name__ == '__main__':
    unittest.main()
