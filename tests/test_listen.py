import unittest

from liblistenbrainz import Listen


class ListenPayloadTestCase(unittest.TestCase):
    def test_payload_does_not_modify_additional_info(self):
        additional_info = {'custom': 'original'}
        listen = Listen('Track', 'Artist', recording_mbid='recording',
                        additional_info=additional_info)

        payload = listen._to_submit_payload()

        self.assertEqual(additional_info, {'custom': 'original'})
        self.assertEqual(listen.additional_info, {'custom': 'original'})
        self.assertEqual(payload['track_metadata']['additional_info'],
                         {'custom': 'original', 'recording_mbid': 'recording'})

    def test_shared_additional_info_does_not_leak_between_listens(self):
        additional_info = {'custom': 'original'}
        first = Listen('First', 'Artist', recording_mbid='first-recording',
                       additional_info=additional_info)
        second = Listen('Second', 'Artist', additional_info=additional_info)

        first._to_submit_payload()
        payload = second._to_submit_payload()

        self.assertEqual(payload['track_metadata']['additional_info'],
                         {'custom': 'original'})

    def test_clearing_a_field_does_not_leave_stale_payload_metadata(self):
        listen = Listen('Track', 'Artist', recording_mbid='recording')
        first_payload = listen._to_submit_payload()
        listen.recording_mbid = None

        second_payload = listen._to_submit_payload()

        self.assertNotIn('additional_info', second_payload['track_metadata'])
        self.assertEqual(first_payload['track_metadata']['additional_info'],
                         {'recording_mbid': 'recording'})
