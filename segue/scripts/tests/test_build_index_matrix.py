"""
Unit tests for build_index matrix. Check if script is returning a vector with all of its elements populated,
using the correct data type. Run it from the project directory with py -m unittest -v scripts.tests.test_build_index_matrix
"""

import unittest
from scripts.build_index_matrix import *

# Define data path
load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")
input_path = f"{DATA_PATH}/miscellaneous/tracks_min.json" # Take the min version for testing

class TestBuildIndexMatrix(unittest.TestCase):
    def test_build_index_matrix(self):
        result = build_index_matrix(input_path)
        # Validate if size is correct
        # Min track version has 4 tracks, then script should return a (4 x 231) matrix
        self.assertEqual(result.shape, (4, 231))
        # Check that type is float32
        self.assertEqual(result.dtype, np.float32)
        # Check that all elements are populated
        self.assertFalse(np.isnan(result).any())    # This tests true if any of the elements in the array is still np.nan
                                                    # Meaning some values are missing

if __name__ == '__main__':
    unittest.main()
