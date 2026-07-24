import unittest
import os
import tempfile
import json
from scripts.extract_audio_features import *

class TestExtractAudioFeatures(unittest.TestCase):
    def setUp(self):
        # Create temporary directories to store files and audio ft
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.audio_ft_tmp = tempfile.TemporaryDirectory()
        self.path = self.tmp_dir.name
        self.audio_ft_path = self.audio_ft_tmp.name

        # Create mock dict resulting from extract_subgenres
        self.mock_tracks = {'abc-123': {'subgenres': ['genre1', 'genre2']}, 'def-456': {'subgenres': ['genre3']}}

    def tearDown(self):
        self.tmp_dir.cleanup()
        self.audio_ft_tmp.cleanup()

    def create_mock_data(self):
        # Create mock JSON data with 2 matching mbids
        for key in self.mock_tracks.keys():
            with open(f"{self.path}/{key}.json", "w") as f:
                json.dump("test", f)

        # Create mock JSON data with no matching mbid
        with open(f"{self.path}/ghi-789.json", "w") as f:
            json.dump("test", f)

        # Zip mock data to .bz2
        with tarfile.open(f"{self.path}/test.tar.bz2", "w:bz2") as tar:
            for file in os.listdir(self.path):
                file_path = os.path.join(self.path, file)
                if file_path.endswith('.json'):
                    # arcname to set an alternative name for the file in the archive
                    tar.add(file_path, arcname=file)

    def test_extract_audio_features(self):
        self.create_mock_data()
        extract_audio_features(self.mock_tracks, self.path, self.audio_ft_path)
        self.assertEqual(len(os.listdir(self.audio_ft_path)), 2) # Only two eligible files should be extracted

if __name__ == '__main__':
    unittest.main()
