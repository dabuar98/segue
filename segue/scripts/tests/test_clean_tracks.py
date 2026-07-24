import unittest
from scripts.clean_tracks import *

class TestCleanTracks(unittest.TestCase):
    def setUp(self):
        # Create base mock dict resulting from extract_metadata
        self.mock_tracks = {
            'abc-123': {
                'subgenres': ['genre1', 'genre2'],
                'title': ['Title A'],
                'artist': ['Artist A'],
                'album': ['Album A'],
                'date': ['Date A'],
            },
            'abc-456': {
                'subgenres': ['genre1', 'genre2'],
                'title': ['Title B'],
                'artist': ['Artist B'],
                'album': ['Album B'],
                'date': ['Date B'],
            },
            'abc-789': {
                'subgenres': ['genre1', 'genre2'],
                'title': ['Title C'],
                'artist': ['Artist C'],
                'album': ['Album C'],
                'date': ['Date C'],
            }
        }

    def tearDown(self):
        # Clean mock tracks
        self.mock_tracks.clear()

    def test_clean_tracks_all_tracks_eligible(self):
        result = clean_tracks(self.mock_tracks)
        # Should return the same elements
        self.assertEqual(result, self.mock_tracks)

    def test_clean_tracks_not_eligible_tracks(self):
        # Adapt base mock tracks so all tracks are missing title and artist
        for key, data in self.mock_tracks.items():
            data['title'] = None
            data['artist'] = None

        result = clean_tracks(self.mock_tracks)
        self.assertEqual(result, {})
        self.assertEqual(len(result), 0)

    def test_clean_tracks_one_track_not_eligible(self):
        # Adapt base mock tracks so track 'abc-123' is not eligible
        self.mock_tracks['abc-123']['title'] = None
        self.mock_tracks['abc-123']['artist'] = None
        result = clean_tracks(self.mock_tracks)

        # Check that ineligible track is not present
        self.assertNotIn('abc-123', list(result.keys()))

        # Check that eligible tracks are present
        self.assertIn('abc-456', list(result.keys()))
        self.assertIn('abc-789', list(result.keys()))
        self.assertEqual(len(result), 2)

if __name__ == '__main__':
    unittest.main()
