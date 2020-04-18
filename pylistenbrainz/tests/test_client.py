# pylistenbrainz - A simple client library for ListenBrainz
# Copyright (C) 2020 Param Singh <iliekcomputers@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os
import pylistenbrainz
import time
import unittest
import uuid

from unittest import mock

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testdata')


class ListenBrainzClientTestCase(unittest.TestCase):

    def setUp(self):
        self.client = pylistenbrainz.ListenBrainz()

    @mock.patch('pylistenbrainz.client.requests.get')
    def test_get_injects_auth_token_if_available(self, mock_requests_get):
        mock_requests_get.return_value = mock.MagicMock()
        self.client._get('/1/user/iliekcomputers/listens')
        mock_requests_get.assert_called_once_with(
            'https://api.listenbrainz.org/1/user/iliekcomputers/listens',
            params={},
            headers={},
        )

        mock_requests_get.reset_mock()
        self.client.is_token_valid = mock.MagicMock(return_value=True)
        auth_token = str(uuid.uuid4())
        self.client.set_auth_token(auth_token)
        self.client._get('/1/user/iliekcomputers/listens')
        mock_requests_get.assert_called_once_with(
            'https://api.listenbrainz.org/1/user/iliekcomputers/listens',
            params={},
            headers={'Authorization': 'Token {}'.format(auth_token)},
        )


    @mock.patch('pylistenbrainz.client.requests.post')
    def test_post_injects_auth_token_if_available(self, mock_requests_post):
        mock_requests_post.return_value = mock.MagicMock()
        self.client._post('/1/user/iliekcomputers/listens')
        mock_requests_post.assert_called_once_with(
            'https://api.listenbrainz.org/1/user/iliekcomputers/listens',
            data=None,
            headers={},
        )

        mock_requests_post.reset_mock()
        self.client.is_token_valid = mock.MagicMock(return_value=True)
        auth_token = str(uuid.uuid4())
        self.client.set_auth_token(auth_token)
        self.client._post('/1/user/iliekcomputers/listens')
        mock_requests_post.assert_called_once_with(
            'https://api.listenbrainz.org/1/user/iliekcomputers/listens',
            data=None,
            headers={'Authorization': 'Token {}'.format(auth_token)},
        )


    def test_client_get_listens(self):
        self.client._get = mock.MagicMock()
        with open(os.path.join(TEST_DATA_DIR, 'get_listens_happy_path_response.json')) as f:
            response_json = json.load(f)
        self.client._get.return_value = response_json
        received_listens = self.client.get_listens('iliekcomputers')
        expected_listens = response_json['payload']['listens']
        self.client._get.assert_called_once_with(
            '/1/user/iliekcomputers/listens',
            params={},
        )
        for i in range(len(expected_listens)):
            self.assertEqual(received_listens[i].listened_at, expected_listens[i]['listened_at'])
            self.assertEqual(received_listens[i].track_name, expected_listens[i]['track_metadata']['track_name'])


    def test_client_get_listens_with_max_ts(self):
        ts = int(time.time())
        self.client._get = mock.MagicMock()
        with open(os.path.join(TEST_DATA_DIR, 'get_listens_happy_path_response.json')) as f:
            response_json = json.load(f)
        self.client._get.return_value = response_json
        received_listens = self.client.get_listens('iliekcomputers', max_ts=ts)
        self.client._get.assert_called_once_with(
            '/1/user/iliekcomputers/listens',
            params={'max_ts': ts},
        )
        expected_listens = response_json['payload']['listens']
        for i in range(len(expected_listens)):
            self.assertEqual(received_listens[i].listened_at, expected_listens[i]['listened_at'])
            self.assertEqual(received_listens[i].track_name, expected_listens[i]['track_metadata']['track_name'])


    def test_client_get_listens_with_min_ts(self):
        ts = int(time.time())
        self.client._get = mock.MagicMock()
        with open(os.path.join(TEST_DATA_DIR, 'get_listens_happy_path_response.json')) as f:
            response_json = json.load(f)
        self.client._get.return_value = response_json
        received_listens = self.client.get_listens('iliekcomputers', min_ts=ts)
        self.client._get.assert_called_once_with(
            '/1/user/iliekcomputers/listens',
            params={'min_ts': ts},
        )
        expected_listens = response_json['payload']['listens']
        for i in range(len(expected_listens)):
            self.assertEqual(received_listens[i].listened_at, expected_listens[i]['listened_at'])
            self.assertEqual(received_listens[i].track_name, expected_listens[i]['track_metadata']['track_name'])


    def test_client_get_listens_with_count(self):
        self.client._get = mock.MagicMock()
        with open(os.path.join(TEST_DATA_DIR, 'get_listens_happy_path_response.json')) as f:
            response_json = json.load(f)
        self.client._get.return_value = response_json
        received_listens = self.client.get_listens('iliekcomputers', count=50)
        self.client._get.assert_called_once_with(
            '/1/user/iliekcomputers/listens',
            params={'count': 50},
        )
        expected_listens = response_json['payload']['listens']
        for i in range(len(expected_listens)):
            self.assertEqual(received_listens[i].listened_at, expected_listens[i]['listened_at'])
            self.assertEqual(received_listens[i].track_name, expected_listens[i]['track_metadata']['track_name'])


    def test_client_get_playing_now(self):
        self.client._get = mock.MagicMock()
        with open(os.path.join(TEST_DATA_DIR, 'get_playing_now_happy_path_response.json')) as f:
            response_json = json.load(f)
        self.client._get.return_value = response_json
        received_listen = self.client.get_playing_now('iliekcomputers')
        self.client._get.assert_called_once_with(
            '/1/user/iliekcomputers/playing-now',
        )
        expected_listen = response_json['payload']['listens'][0]
        self.assertIsNotNone(received_listen)
        self.assertIsNone(received_listen.listened_at)
        self.assertEqual(received_listen.track_name, expected_listen['track_metadata']['track_name'])


    def test_client_get_playing_now_no_listen(self):
        self.client._get = mock.MagicMock()
        with open(os.path.join(TEST_DATA_DIR, 'no_playing_now.json')) as f:
            response_json = json.load(f)
        self.client._get.return_value = response_json
        received_listen = self.client.get_playing_now('iliekcomputers')
        self.client._get.assert_called_once_with(
            '/1/user/iliekcomputers/playing-now',
        )
        self.assertIsNone(received_listen)
