import unittest
import tempfile
import json
from scripts.extract_metadata import *

class TestExtractMetadata(unittest.TestCase):
    def setUp(self):
        # Create temporary directory to store audio features
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.path = self.tmp_dir.name

        # Create base mock audio features
        self.mock_audioft = {
            "tonal" : {},
            "metadata": {},
            "rhythm" : {},
            "lowlevel" : {}
        }

        # Create mock dict resulting from extract_subgenres
        self.mock_tracks = {'abc-123': {'subgenres': ['genre1', 'genre2']}}

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_metadata_extraction_with_all_fields(self):
        # Add mock metadata
        self.mock_audioft['metadata']['tags'] = {
            "title": ["In a While"],
            "artist": ["Ben Klock"],
            "album": ["One"],
            "date": ["2005"]
        }

        # Create mock JSON containing the audio features
        with open(f"{self.path}/abc-123.json", "w") as f:
            json.dump(self.mock_audioft, f)

        extract_metadata(self.mock_tracks, self.path)
        # Check previous fields are still present
        self.assertEqual(['genre1', 'genre2'], self.mock_tracks['abc-123']['subgenres'])
        # Check that title, artist, album, date are
        self.assertEqual(['In a While'], self.mock_tracks['abc-123']['title'])
        self.assertEqual(['Ben Klock'], self.mock_tracks['abc-123']['artist'])
        self.assertEqual(['One'], self.mock_tracks['abc-123']['album'])
        self.assertEqual(['2005'], self.mock_tracks['abc-123']['date'])

    def test_metadata_extraction_without_fields(self):
        self.mock_audioft['metadata']['tags'] ={}

        # Create mock JSON containing the audio features
        with open(f"{self.path}/abc-123.json", "w") as f:
            json.dump(self.mock_audioft, f)

        extract_metadata(self.mock_tracks, self.path)
        # Check previous fields are still present
        self.assertEqual(['genre1', 'genre2'], self.mock_tracks['abc-123']['subgenres'])
        # Check that title, artist, album, date are
        self.assertEqual(None, self.mock_tracks['abc-123']['title'])
        self.assertEqual(None, self.mock_tracks['abc-123']['artist'])
        self.assertEqual(None, self.mock_tracks['abc-123']['album'])
        self.assertEqual(None, self.mock_tracks['abc-123']['date'])


    def test_metadata_extraction_without_tags(self):
        # Create mock JSON containing the audio features
        with open(f"{self.path}/abc-123.json", "w") as f:
            json.dump(self.mock_audioft, f)

        extract_metadata(self.mock_tracks, self.path)
        # Check previous fields are still present
        self.assertEqual(['genre1', 'genre2'], self.mock_tracks['abc-123']['subgenres'])
        # Check that title, artist, album, date are
        self.assertEqual(None, self.mock_tracks['abc-123']['title'])
        self.assertEqual(None, self.mock_tracks['abc-123']['artist'])
        self.assertEqual(None, self.mock_tracks['abc-123']['album'])
        self.assertEqual(None, self.mock_tracks['abc-123']['date'])

    def test_metadata_extraction_without_title(self):
        # Add mock metadata
        self.mock_audioft['metadata']['tags'] = {
            "artist": ["Ben Klock"],
            "album": ["One"],
            "date": ["2005"]
        }

        # Create mock JSON containing the audio features
        with open(f"{self.path}/abc-123.json", "w") as f:
            json.dump(self.mock_audioft, f)

        extract_metadata(self.mock_tracks, self.path)
        # Check previous fields are still present
        self.assertEqual(['genre1', 'genre2'], self.mock_tracks['abc-123']['subgenres'])
        # Check that title, artist, album, date are
        self.assertEqual(None, self.mock_tracks['abc-123']['title'])
        self.assertEqual(['Ben Klock'], self.mock_tracks['abc-123']['artist'])
        self.assertEqual(['One'], self.mock_tracks['abc-123']['album'])
        self.assertEqual(['2005'], self.mock_tracks['abc-123']['date'])

    def test_metadata_extraction_without_artist(self):
        # Add mock metadata
        self.mock_audioft['metadata']['tags'] = {
            "title": ["In a While"],
            "album": ["One"],
            "date": ["2005"]
        }

        # Create mock JSON containing the audio features
        with open(f"{self.path}/abc-123.json", "w") as f:
            json.dump(self.mock_audioft, f)

        extract_metadata(self.mock_tracks, self.path)
        # Check previous fields are still present
        self.assertEqual(['genre1', 'genre2'], self.mock_tracks['abc-123']['subgenres'])
        # Check that title, artist, album, date are
        self.assertEqual(["In a While"], self.mock_tracks['abc-123']['title'])
        self.assertEqual(None, self.mock_tracks['abc-123']['artist'])
        self.assertEqual(['One'], self.mock_tracks['abc-123']['album'])
        self.assertEqual(['2005'], self.mock_tracks['abc-123']['date'])

    def test_metadata_extraction_without_album(self):
        # Add mock metadata
        self.mock_audioft['metadata']['tags'] = {
            "title": ["In a While"],
            "artist": ["Ben Klock"],
            "date": ["2005"]
        }

        # Create mock JSON containing the audio features
        with open(f"{self.path}/abc-123.json", "w") as f:
            json.dump(self.mock_audioft, f)

        extract_metadata(self.mock_tracks, self.path)
        # Check previous fields are still present
        self.assertEqual(['genre1', 'genre2'], self.mock_tracks['abc-123']['subgenres'])
        # Check that title, artist, album, date are
        self.assertEqual(['In a While'], self.mock_tracks['abc-123']['title'])
        self.assertEqual(['Ben Klock'], self.mock_tracks['abc-123']['artist'])
        self.assertEqual(None, self.mock_tracks['abc-123']['album'])
        self.assertEqual(['2005'], self.mock_tracks['abc-123']['date'])

    def test_metadata_extraction_without_date(self):
        # Add mock metadata
        self.mock_audioft['metadata']['tags'] = {
            "title": ["In a While"],
            "artist": ["Ben Klock"],
            "album": ["One"],
        }

        # Create mock JSON containing the audio features
        with open(f"{self.path}/abc-123.json", "w") as f:
            json.dump(self.mock_audioft, f)

        extract_metadata(self.mock_tracks, self.path)
        # Check previous fields are still present
        self.assertEqual(['genre1', 'genre2'], self.mock_tracks['abc-123']['subgenres'])
        # Check that title, artist, album, date are
        self.assertEqual(['In a While'], self.mock_tracks['abc-123']['title'])
        self.assertEqual(['Ben Klock'], self.mock_tracks['abc-123']['artist'])
        self.assertEqual(['One'], self.mock_tracks['abc-123']['album'])
        self.assertEqual(None, self.mock_tracks['abc-123']['date'])

if __name__ == '__main__':
    unittest.main()
