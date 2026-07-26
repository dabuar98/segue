"""
Test whether extract_query_descriptors is returning the following elements, necessary to build query vector:
tonal.hpcp.mean -> 36 elements
tonal.key_key -> 1 element (string) (in older versions) | tonal.key_edma.key -> 1 element (string) (Supported in version 2.1b6.dev1389)
tonal.key_scale -> 1 element (string) | tonal.key_edma.scale -> 1 element (string) (Supported in version 2.1b6.dev1389)
tonal.key_strength -> 1 element | tonal.key_edma.strength -> 1 element (string) (Supported in version 2.1b6.dev1389)
lowlevel.mfcc.mean -> 13 elements
lowlevel.mfcc.cov -> 13 elements
lowlevel.spectral_centroid.mean -> 1 element
lowlevel.spectral_rolloff.mean -> 1 element
lowlevel.spectral_flux.mean -> 1 element
lowlevel.zerocrossingrate.mean -> 1 element
lowlevel.zerocrossingrate.var -> 1 element
rhythm.bpm -> 1 element
rhythm.danceability -> 1 element
rhythm.beats_loudness.mean -> 1 element
rhythm.beats_loudness.var -> 1 element
rhythm.onset_rate -> 1 element
"""

import os
import unittest
from scripts.extract_query_descriptors import *

path_to_audio = os.path.join(os.path.dirname(__file__), 'In a While (Original Mix).mp3')
result = extract_query_descriptors(path_to_audio)

# Test that Essentia is returning the necessary information to build a query vector
class TestExtractQueryDescriptors(unittest.TestCase):
    def setUp(self):
        # Compute result once and make it available to test class
        self.result = result

    # Check if primary keys are present
    def test_extract_query_descriptors_keys_present(self):
        self.assertIn('tonal', list(self.result.keys()))
        self.assertIn('lowlevel', list(self.result.keys()))
        self.assertIn('rhythm', list(self.result.keys()))

    # Check if the necessary tonal values are present
    def test_extract_query_descriptors_tonal_values_present(self):
        self.assertIsNot(self.result.get('tonal').get('hpcp').get('mean'), None)
        self.assertIsNot(self.result.get('tonal').get('key_edma').get('key'), None)
        self.assertIsNot(self.result.get('tonal').get('key_edma').get('scale'), None)
        self.assertIsNot(self.result.get('tonal').get('key_edma').get('strength'), None)

    # Check if the necessary low-level values are present
    def test_extract_query_descriptors_lowlevel_values_present(self):
        self.assertIsNot(self.result.get('lowlevel').get('mfcc').get('mean'), None)
        self.assertIsNot(self.result.get('lowlevel').get('mfcc').get('cov'), None)
        self.assertIsNot(self.result.get('lowlevel').get('spectral_centroid').get('mean'), None)
        self.assertIsNot(self.result.get('lowlevel').get('spectral_rolloff').get('mean'), None)
        self.assertIsNot(self.result.get('lowlevel').get('spectral_flux').get('mean'), None)
        self.assertIsNot(self.result.get('lowlevel').get('zerocrossingrate').get('mean'), None)
        self.assertIsNot(self.result.get('lowlevel').get('zerocrossingrate').get('var'), None)

    # Check if the necessary rhythmical values are present
    def test_extract_query_descriptors_rhythm_values_present(self):
        self.assertIsNot(self.result.get('rhythm').get('bpm'), None)
        self.assertIsNot(self.result.get('rhythm').get('danceability'), None)
        self.assertIsNot(self.result.get('rhythm').get('beats_loudness').get('mean'), None)
        self.assertIsNot(self.result.get('rhythm').get('beats_loudness').get('var'), None)
        self.assertIsNot(self.result.get('rhythm').get('onset_rate'), None)

    # Check that grouped descriptors contain the number of values
    def test_extract_query_descriptors_validate_grouped_values(self):
        # These values should be assigned a list
        self.assertIsInstance(self.result.get('tonal').get('hpcp').get('mean'), list)
        self.assertIsInstance(self.result.get('lowlevel').get('mfcc').get('mean'), list)
        self.assertIsInstance(self.result.get('lowlevel').get('mfcc').get('cov'), list)
        self.assertEqual(len(self.result.get('tonal').get('hpcp').get('mean')), 36)
        self.assertEqual(len(self.result.get('lowlevel').get('mfcc').get('mean')), 13)
        self.assertEqual(len(self.result.get('lowlevel').get('mfcc').get('cov')), 13)

    # Check that scalar descriptors contain only 1 element
    # Test for data type
    def test_extract_query_descriptors_validate_single_values(self):
        self.assertIsInstance(self.result.get('tonal').get('key_edma').get('key'), str)
        self.assertIsInstance(self.result.get('tonal').get('key_edma').get('scale'), str)
        self.assertIsInstance(self.result.get('tonal').get('key_edma').get('strength'), float)
        self.assertIsInstance(self.result.get('lowlevel').get('spectral_centroid').get('mean'), float)
        self.assertIsInstance(self.result.get('lowlevel').get('spectral_rolloff').get('mean'), float)
        self.assertIsInstance(self.result.get('lowlevel').get('spectral_flux').get('mean'), float)
        self.assertIsInstance(self.result.get('lowlevel').get('zerocrossingrate').get('mean'), float)
        self.assertIsInstance(self.result.get('lowlevel').get('zerocrossingrate').get('var'), float)
        self.assertIsInstance(self.result.get('rhythm').get('bpm'), float)
        self.assertIsInstance(self.result.get('rhythm').get('danceability'), float)
        self.assertIsInstance(self.result.get('rhythm').get('beats_loudness').get('mean'), float)
        self.assertIsInstance(self.result.get('rhythm').get('beats_loudness').get('var'), float)
        self.assertIsInstance(self.result.get('rhythm').get('onset_rate'), float)

if __name__ == '__main__':
    unittest.main()
