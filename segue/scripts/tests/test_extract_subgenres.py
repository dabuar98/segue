import os
import unittest
import tempfile
from scripts.extract_subgenres import *

# To test py -m unittest tests.extract_subgenres_test

# Create mock data simulating genre dataset with different characteristics
data_with_one_eligible_track = [
    {
        'id': 'abc-123',
        'rid': 'abc-123',
        'genre1' : 'electronic',
        'genre2' : 'electronic---ambient',
        'genre3' : 'electronic---jazz',
        'genre4' : 'electronic---experimental',
        'genre5' : 'electronic---acid jazz',
    },
    {
        'id': 'def-456',
        'rid': 'def-456',
        'genre1': 'electronic',
        'genre2': 'rock---hardcore',
        'genre3': 'electronic---jazz',
        'genre4': '',
        'genre5': '',
    }
]

data_with_no_eligible_tracks = [
    {
        'id': 'def-456',
        'rid': 'def-456',
        'genre1': 'electronic',
        'genre2': 'rock---hardcore',
        'genre3': 'electronic---jazz',
        'genre4': '',
        'genre5': '',
    },
    {
        'id': 'fkl-789',
        'rid': 'fkl-789',
        'genre1': 'classical---contemporary',
        'genre2': 'electronic---minimal',
        'genre3': 'electronic---experimental',
        'genre4': '',
        'genre5': '',
    },
]

data_with_two_eligible_tracks = [
    {
        'id': 'abc-123',
        'rid': 'abc-123',
        'genre1' : 'electronic',
        'genre2' : 'electronic---ambient',
        'genre3' : 'electronic---jazz',
        'genre4' : 'electronic---experimental',
        'genre5' : 'electronic---acid jazz',
    },
    {
        'id': 'def-456',
        'rid': 'def-456',
        'genre1': 'electronic',
        'genre2': 'electronic---hardcore',
        'genre3': 'electronic---jazz',
        'genre4': '',
        'genre5': '',
    }
]

data_with_one_eligible_track_merging = [
    {
        'id': 'abc-123',
        'rid': 'abc-123',
        'genre1' : 'electronic',
        'genre2' : 'electronic---ambient',
        'genre3' : 'electronic---jazz',
        'genre4' : 'electronic---experimental',
        'genre5' : '',
    },
    {
        'id': 'abc-123',
        'rid': 'abc-123',
        'genre1': 'electronic',
        'genre2': 'electronic---jazz',
        'genre3': '',
        'genre4': '',
        'genre5': 'electronic---noise',
    },
]

# Tests for extract_subgenres_electornic_tracks.py
class TestExtractSubgenres(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.path = self.tmp_dir.name

    def tearDown(self):
        self.tmp_dir.cleanup()

    # Receives a dict with recordingmbid (id), releasegroupmbid (rid), genres (up to 5)
    def _write_genre_tsv(self, data={}):
        with open(os.path.join(self.path, "genre.tsv"), 'w') as f:
            f.write("recordingmbid\treleasegroupmbid\tgenre1\tgenre2\tgenre3\tgenre4\tgenre5\n")
            for d in data:
                f.write(
                    f"{d['id']}\t{d['rid']}\t{d['genre1']}\t{d['genre2']}\t{d['genre3']}\t{d['genre4']}\t{d['genre5']}\n")

    def test_extract_genres_one_eligible_track(self):
        self._write_genre_tsv(data_with_one_eligible_track)
        result = extract_subgenres(self.path)
        self.assertEqual(len(result), 1)
        self.assertEqual(list(result.keys()), ['abc-123'])
        # Since adding items to a set does not preserve insertion order
        # Test if the genre is in subgenres (regardless of the order)
        self.assertIn('ambient', result['abc-123']['subgenres'])
        self.assertIn('jazz', result['abc-123']['subgenres'])
        self.assertIn('experimental', result['abc-123']['subgenres'])
        self.assertIn('acid jazz', result['abc-123']['subgenres'])
        self.assertEqual(len(result['abc-123']['subgenres']), 4)

    def test_extract_subgenres_no_eligible_tracks(self):
        self._write_genre_tsv(data_with_no_eligible_tracks)
        result = extract_subgenres(self.path)
        self.assertEqual(len(result), 0)

    def test_extract_subgenres_two_eligible_tracks(self):
        self._write_genre_tsv(data_with_two_eligible_tracks)
        result = extract_subgenres(self.path)
        self.assertEqual(len(result), 2)
        # Check if both keys are the mbids
        self.assertEqual(list(result.keys()), ['abc-123','def-456'])
        self.assertIn('ambient', result['abc-123']['subgenres'])
        self.assertIn('jazz', result['abc-123']['subgenres'])
        self.assertIn('experimental', result['abc-123']['subgenres'])
        self.assertIn('acid jazz', result['abc-123']['subgenres'])
        self.assertEqual(len(result['abc-123']['subgenres']), 4)
        self.assertIn('hardcore', result['def-456']['subgenres'])
        self.assertIn('jazz', result['def-456']['subgenres'])
        self.assertEqual(len(result['def-456']['subgenres']), 2)

    def test_extract_subgenres_merging(self):
        self._write_genre_tsv(data_with_one_eligible_track_merging)
        result = extract_subgenres(self.path)
        self.assertEqual(len(result), 1)
        self.assertEqual(list(result.keys()), ['abc-123'])
        self.assertIn('ambient', result['abc-123']['subgenres'])
        self.assertIn('jazz', result['abc-123']['subgenres'])
        self.assertIn('experimental', result['abc-123']['subgenres'])
        self.assertIn('noise', result['abc-123']['subgenres'])
        self.assertEqual(len(result['abc-123']['subgenres']), 4)

if __name__ == '__main__':
    unittest.main()
