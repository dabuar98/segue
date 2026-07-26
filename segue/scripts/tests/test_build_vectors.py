"""
Unit tests for build_index_vector and build_query_vector
Run it from the project directory with py -m unittest -v scripts.tests.test_build_vectors
"""
import os
import unittest

import numpy as np
from dotenv import load_dotenv
from scripts.build_query_vector import build_query_vector
from scripts.build_index_vector import build_index_vector

# Inject .env values to os.environ
load_dotenv()

# Define paths and compute result once (same result for all test suites
DATA_PATH = os.getenv("DATA_PATH")

class TestBuildVectors(unittest.TestCase):
    def test_build_query_vector(self):
        result = build_query_vector(f"{DATA_PATH}/sample.mp3") # Receives an audio file
        # Test dimension
        self.assertEqual(result.shape, (1, 231))
        # Test key mapping (key is the first element of the vector)
        self.assertTrue(result[0, 0] in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        # Script should return a np array of type float32
        self.assertIsInstance(result, np.ndarray)
        self.assertTrue(i is np.float32 for i in result[0, :]) # Check each object is of the proper type
        # Test key scale mapping (key scale is the second element of the vector)
        self.assertTrue(result[0, 1] in [0, 1])

    def test_build_index_vector(self):
        result = build_index_vector(f"{DATA_PATH}/audio_features_sample.json") # Receives a JSON file
        # Test dimension
        self.assertEqual(result.shape, (1, 231))
        # Test key mapping (key is the first element of the vector)
        self.assertTrue(result[0, 0] in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        # Script should return a np array of type float32
        self.assertIsInstance(result, np.ndarray)
        self.assertTrue(i is np.float32 for i in result[0, :]) # Check each object is of the proper type
        # Test key mapping (key is the first element of the vector)
        self.assertTrue(result[0, 0] in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        # Test key scale mapping (key scale is the second element of the vector)
        self.assertTrue(result[0, 1] in [0, 1])

if __name__ == '__main__':
    unittest.main()
