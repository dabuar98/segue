import io
import os
import tempfile
import uuid
import wave
from unittest.mock import patch
import faiss
import numpy as np
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from api.models import Tracks, Subgenres, TrackSubgenreLink
from api.query_cache import get_query, set_query, PENDING, READY, FAILED
from app.celery.tasks import compute_query

# Keep the tests away from the Redis instance used by the running application
LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


def make_wav(name='track.wav', size_mb=2):
    """
    Builds a short silent WAV file in memory so libmagic detects it as audio
    Args:
        name: file name
        size_mb: size of the file in MB

    Returns:
        SimpleUploadedFile: representation of a file (mock)

    """
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(b'\x00' * (size_mb * 1024 * 1024))
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='audio/wav')


def make_index(vectors):
    vectors = np.array(vectors, dtype=np.float32)
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index


@override_settings(CACHES=LOCMEM_CACHE)
class TestCreateQuery(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse('create_query')

        # Replace the Celery task so no worker or broker is needed
        self.task_patcher = patch('api.views.compute_query')
        self.mock_task = self.task_patcher.start()

    def tearDown(self):
        self.task_patcher.stop()
        # The mocked task never removes the uploaded file, so do it here
        for call in self.mock_task.delay.call_args_list:
            tmp_path = call.args[1]
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def post(self, **data):
        data.setdefault('track', make_wav())
        return self.client.post(self.url, data)

    def test_returns_query_id_and_pending_status(self):
        response = self.post()
        self.assertEqual(202, response.status_code)
        body = response.json()
        self.assertEqual(PENDING, body['status'])
        # Check the id is a valid UUID
        uuid.UUID(body['query_id'])

    def test_query_is_stored_as_pending(self):
        query_id = self.post(descriptor_set='bogdanov').json()['query_id']
        self.assertEqual({'status': PENDING, 'descriptor_set': 'bogdanov', 'vector': None}, get_query(query_id))

    def test_task_receives_query_id_file_and_descriptor_set(self):
        query_id = self.post(descriptor_set='tzanetakis').json()['query_id']
        task_query_id, tmp_path, descriptor_set = self.mock_task.delay.call_args.args
        self.assertEqual(query_id, task_query_id)
        self.assertEqual('tzanetakis', descriptor_set)
        # The uploaded file is kept for the worker, with its original extension
        self.assertTrue(os.path.exists(tmp_path))
        self.assertTrue(tmp_path.endswith('.wav'))

    def test_default_descriptor_set_is_schedl(self):
        self.post()
        self.assertEqual('schedl', self.mock_task.delay.call_args.args[2])

    def test_each_upload_gets_a_different_query_id(self):
        self.assertNotEqual(self.post().json()['query_id'], self.post().json()['query_id'])

    def test_invalid_descriptor_set(self):
        response = self.post(descriptor_set='unknown')
        self.assertEqual(400, response.status_code)
        self.assertIn('descriptor_set must be one of', response.json()['error'])
        self.mock_task.delay.assert_not_called()

    def test_missing_track(self):
        response = self.client.post(self.url, {'descriptor_set': 'schedl'})
        self.assertEqual(400, response.status_code)
        self.assertEqual('track is required', response.json()['error'])

    def test_non_audio_file_rejected_and_removed(self):
        text_file = SimpleUploadedFile('notes.txt', b'just some text', content_type='text/plain')
        with patch('api.views.os.remove', wraps=os.remove) as mock_remove:
            response = self.post(track=text_file)
        self.assertEqual(400, response.status_code)
        self.assertEqual('only audio files are supported', response.json()['error'])
        self.mock_task.delay.assert_not_called()
        mock_remove.assert_called_once()

    def test_audio_file_exceeded_size_limit(self):
        larger_audio = make_wav(size_mb=21)
        response = self.post(track=larger_audio)
        self.assertEqual(400, response.status_code)
        self.assertEqual('uploaded file exceeds the 20MB size limit', response.json()['error'])

    def test_non_audio_file_with_audio_extension_rejected(self):
        # MIME type is detected from content, not from the file name
        fake_audio = SimpleUploadedFile('fake.mp3', b'just some text', content_type='audio/mpeg')
        response = self.post(track=fake_audio)
        self.assertEqual(400, response.status_code)
        self.assertEqual('only audio files are supported', response.json()['error'])

    def test_broker_failure_cleans_up(self):
        self.mock_task.delay.side_effect = ConnectionError('broker unreachable')
        with patch('api.views.os.remove', wraps=os.remove) as mock_remove, \
                patch('api.views.delete_query') as mock_delete, \
                self.assertLogs('api.views', level='ERROR'):
            response = self.post()
        self.assertEqual(500, response.status_code)
        self.assertEqual('system error', response.json()['error'])
        mock_remove.assert_called_once()
        mock_delete.assert_called_once()

    def test_get_not_allowed(self):
        self.assertEqual(405, self.client.get(self.url).status_code)


@override_settings(CACHES=LOCMEM_CACHE)
class TestQueryStatus(TestCase):
    def setUp(self):
        cache.clear()
        self.query_id = str(uuid.uuid4())
        self.url = reverse('query_status', args=[self.query_id])

    def test_unknown_query(self):
        response = self.client.get(self.url)
        self.assertEqual(404, response.status_code)
        self.assertEqual('query not found or expired', response.json()['error'])

    def test_reports_each_status(self):
        for status in [PENDING, READY, FAILED]:
            with self.subTest(status=status):
                set_query(self.query_id, status, 'schedl', [[1.0]] if status == READY else None)
                self.assertEqual(
                    {'query_id': self.query_id, 'status': status, 'descriptor_set': 'schedl'},
                    self.client.get(self.url).json()
                )

    def test_vector_is_not_exposed(self):
        set_query(self.query_id, READY, 'schedl', [[1.0, 0.0]])
        self.assertNotIn('vector', self.client.get(self.url).json())

    def test_invalid_query_id_is_not_routed(self):
        self.assertEqual(404, self.client.get('/api/queries/not-a-uuid/').status_code)

    def test_post_not_allowed(self):
        self.assertEqual(405, self.client.post(self.url).status_code)


@override_settings(CACHES=LOCMEM_CACHE)
class TestSimilar(TestCase):
    def setUp(self):
        cache.clear()
        self.query_id = str(uuid.uuid4())
        self.url = reverse('similar', args=[self.query_id])

        # Create mock index vectors, ordered by decreasing similarity to the query vector [1, 0, 0, 0]
        self.index = make_index([
            [1.0, 0.0, 0.0, 0.0],
            [0.9, 0.1, 0.0, 0.0],
            [0.7, 0.3, 0.0, 0.0],
            [0.5, 0.5, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ])

        # Same vectors in reverse order, to check the index of the stored descriptor set is used
        self.reversed_index = make_index([
            [0.0, 1.0, 0.0, 0.0],
            [0.5, 0.5, 0.0, 0.0],
            [0.7, 0.3, 0.0, 0.0],
            [0.9, 0.1, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
        ])

        # The view maps faiss positions to Tracks ids, so create tracks with matching ids
        genres = ['techno', 'house', 'minimal techno', 'house', 'techno']
        for i, genre in enumerate(genres):
            track = Tracks.objects.create(
                id=i, mbid=f'mbid-{i}', title=f'title-{i}', artist=f'artist-{i}', album=f'album-{i}', date='2005'
            )
            subgenre = Subgenres.objects.create(mbid=track.mbid, genre=genre)
            TrackSubgenreLink.objects.create(track=track, subgenre=subgenre)

        # Replace the faiss indexes loaded from disk with the mock indexes
        mock_sets = {'schedl': self.index, 'tzanetakis': self.index, 'bogdanov': self.reversed_index}
        self.sets_patcher = patch.dict('api.views.DESCRIPTOR_SETS', mock_sets, clear=True)
        self.sets_patcher.start()

        # Store a computed query vector, as the Celery worker would
        set_query(self.query_id, READY, 'schedl', [[1.0, 0.0, 0.0, 0.0]])

    def tearDown(self):
        self.sets_patcher.stop()

    def get(self, **params):
        return self.client.get(self.url, params)

    def mbids(self, response):
        return [t['mbid'] for t in response.json()]

    def test_returns_most_similar_tracks_in_order(self):
        response = self.get(n=3)
        self.assertEqual(200, response.status_code)
        self.assertEqual(['mbid-0', 'mbid-1', 'mbid-2'], self.mbids(response))

    def test_response_contains_track_fields(self):
        self.assertEqual([{
            'mbid': 'mbid-0',
            'title': 'title-0',
            'artist': 'artist-0',
            'album': 'album-0',
            'date': '2005',
            'subgenres': ['techno'],
        }], self.get(n=1).json())

    def test_default_n_returns_all_tracks_when_index_is_smaller(self):
        # Default n is 20, but the index only holds 5 vectors
        response = self.get()
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.json()))

    def test_n_zero_returns_empty_list(self):
        response = self.get(n=0)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.json())

    def test_similarity_hidden_by_default(self):
        for track in self.get(n=2).json():
            self.assertNotIn('similarity', track)

    def test_show_sim_adds_similarity(self):
        tracks = self.get(n=2, show_sim='TRUE').json()
        self.assertAlmostEqual(1.0, tracks[0]['similarity'], places=5)
        self.assertGreater(tracks[0]['similarity'], tracks[1]['similarity'])

    def test_subgenre_filter(self):
        self.assertEqual(['mbid-1', 'mbid-3'], self.mbids(self.get(n=5, subgenre='house')))

    def test_subgenre_filter_matches_partially_and_ignores_case(self):
        # 'Techno' should match both 'techno' and 'minimal techno'
        self.assertEqual(['mbid-0', 'mbid-2', 'mbid-4'], self.mbids(self.get(n=5, subgenre='Techno')))

    def test_subgenre_filter_widens_search_to_fill_n(self):
        # The only 'house' tracks are at positions 1 and 3, beyond the first n=2 candidates
        self.assertEqual(['mbid-1', 'mbid-3'], self.mbids(self.get(n=2, subgenre='house')))

    def test_subgenre_filter_without_matches_returns_empty_list(self):
        response = self.get(n=3, subgenre='jazz')
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.json())

    def test_filters_can_be_reapplied_to_the_same_query(self):
        self.assertEqual(['mbid-0', 'mbid-1'], self.mbids(self.get(n=2)))
        self.assertEqual(['mbid-1'], self.mbids(self.get(n=1, subgenre='house')))
        self.assertEqual(['mbid-0', 'mbid-1', 'mbid-2'], self.mbids(self.get(n=3)))

    def test_uses_index_of_stored_descriptor_set(self):
        set_query(self.query_id, READY, 'bogdanov', [[1.0, 0.0, 0.0, 0.0]])
        self.assertEqual(['mbid-4', 'mbid-3'], self.mbids(self.get(n=2)))

    def test_unknown_query(self):
        response = self.client.get(reverse('similar', args=[str(uuid.uuid4())]))
        self.assertEqual(404, response.status_code)
        self.assertEqual('query not found or expired', response.json()['error'])

    def test_pending_query(self):
        set_query(self.query_id, PENDING, 'schedl')
        response = self.get()
        self.assertEqual(409, response.status_code)
        self.assertEqual('query is still being processed', response.json()['error'])

    def test_failed_query(self):
        set_query(self.query_id, FAILED, 'schedl')
        response = self.get()
        self.assertEqual(422, response.status_code)
        self.assertEqual('audio feature extraction failed', response.json()['error'])

    def test_non_integer_n(self):
        for n in ['abc', '2.5', '']:
            with self.subTest(n=n):
                response = self.get(n=n)
                self.assertEqual(400, response.status_code)
                self.assertEqual('n must be a integer', response.json()['error'])

    def test_negative_n(self):
        response = self.get(n=-1)
        self.assertEqual(400, response.status_code)
        self.assertEqual('n must be a positive integer', response.json()['error'])

    def test_n_above_limit(self):
        response = self.get(n=51)
        self.assertEqual(400, response.status_code)
        self.assertEqual('n must be less than 50', response.json()['error'])

    def test_n_at_limit_is_accepted(self):
        self.assertEqual(200, self.get(n=50).status_code)

    def test_invalid_show_sim(self):
        response = self.get(show_sim='yes')
        self.assertEqual(400, response.status_code)
        self.assertEqual('dist must be a boolean', response.json()['error'])

    def test_database_error_returns_system_error(self):
        with patch('api.views.Tracks.objects.get', side_effect=RuntimeError('db down')), \
                self.assertLogs('api.views', level='ERROR'):
            response = self.get(n=1)
        self.assertEqual(500, response.status_code)
        self.assertEqual('system error', response.json()['error'])

    def test_post_not_allowed(self):
        self.assertEqual(405, self.client.post(self.url).status_code)


@override_settings(CACHES=LOCMEM_CACHE)
class TestComputeQueryTask(TestCase):
    def setUp(self):
        cache.clear()
        self.query_id = str(uuid.uuid4())
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            self.tmp_path = tmp.name

        # Replace the audio feature extraction, tested in scripts/tests
        self.extract_patcher = patch('app.celery.tasks.extract_audio_features')
        self.mock_extract = self.extract_patcher.start()

    def tearDown(self):
        self.extract_patcher.stop()
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    def test_stores_vector_as_ready(self):
        self.mock_extract.return_value = [[0.1, 0.2]]
        compute_query(self.query_id, self.tmp_path, 'bogdanov')
        self.mock_extract.assert_called_once_with(self.tmp_path, 'bogdanov')
        self.assertEqual({'status': READY, 'descriptor_set': 'bogdanov', 'vector': [[0.1, 0.2]]}, get_query(self.query_id))

    def test_removes_uploaded_file(self):
        self.mock_extract.return_value = [[0.1, 0.2]]
        compute_query(self.query_id, self.tmp_path, 'schedl')
        self.assertFalse(os.path.exists(self.tmp_path))

    def test_failure_marks_query_as_failed_and_removes_file(self):
        self.mock_extract.side_effect = RuntimeError('corrupt audio')
        with self.assertRaises(RuntimeError):
            compute_query(self.query_id, self.tmp_path, 'schedl')
        self.assertEqual({'status': FAILED, 'descriptor_set': 'schedl', 'vector': None}, get_query(self.query_id))
        self.assertFalse(os.path.exists(self.tmp_path))
