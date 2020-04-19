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
import requests

from pylistenbrainz import errors
from pylistenbrainz.listen import LISTEN_TYPE_IMPORT, LISTEN_TYPE_PLAYING_NOW, LISTEN_TYPE_SINGLE
from pylistenbrainz.utils import _validate_submit_listens_payload, _convert_api_payload_to_listen
from urllib.parse import urljoin


API_BASE_URL = 'https://api.listenbrainz.org'

class ListenBrainz:

    def __init__(self):
        self._auth_token = None


    def _require_auth_token(self):
        if not self._auth_token:
            raise errors.AuthTokenRequiredException


    def _get(self, endpoint, params=None, headers=None):
        if not params:
            params = {}
        if not headers:
            headers = {}
        if self._auth_token:
            headers['Authorization'] = 'Token {}'.format(self._auth_token)

        response = requests.get(
           urljoin(API_BASE_URL, endpoint),
           params=params,
           headers=headers,
        )
        response.raise_for_status()
        return response.json()


    def _post(self, endpoint, data=None, headers=None):
        if not headers:
            headers = {}
        if self._auth_token:
            headers['Authorization'] = 'Token {}'.format(self._auth_token)
        response = requests.post(
           urljoin(API_BASE_URL, endpoint),
           data=data,
           headers=headers,
        )
        response.raise_for_status()
        return response.json()


    def set_auth_token(self, auth_token):
        if self.is_token_valid(auth_token):
            self._auth_token = auth_token
        else:
            raise errors.InvalidAuthTokenException


    def _post_submit_listens(self, listens, listen_type):
        self._require_auth_token()
        _validate_submit_listens_payload(listen_type, listens)
        listen_payload = [listen.to_submit_payload() for listen in listens]
        submit_json = {
            'listen_type': listen_type,
            'payload': listen_payload
        }
        return self._post(
            '/1/submit-listens',
            data=json.dumps(submit_json),
        )


    def submit_multiple_listens(self, listens):
        return self._post_submit_listens(listens, LISTEN_TYPE_IMPORT)


    def submit_single_listen(self, listen):
        return self._post_submit_listens([listen], LISTEN_TYPE_SINGLE)


    def submit_playing_now(self, listen):
        return self._post_submit_listens([listen], LISTEN_TYPE_PLAYING_NOW)


    def is_token_valid(self, token):
        data = self._get(
            '/1/validate-token',
            params={'token': token},
        )
        return data['valid']


    def get_playing_now(self, username):
        data = self._get('/1/user/{username}/playing-now'.format(username=username))
        listens = data['payload']['listens']
        if len(listens) > 0: # should never be greater than 1
            return _convert_api_payload_to_listen(listens[0])
        return None


    def get_listens(self, username, max_ts=None, min_ts=None, count=None):
        params = {}
        if max_ts is not None:
            params['max_ts'] = max_ts
        if min_ts is not None:
            params['min_ts'] = min_ts
        if count is not None:
            params['count'] = count

        data = self._get(
            '/1/user/{username}/listens'.format(username=username),
            params=params,
        )
        listens = data['payload']['listens']
        return [_convert_api_payload_to_listen(listen_data) for listen_data in listens]
