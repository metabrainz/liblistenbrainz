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

from pylistenbrainz.utils import _validate_submit_listens_payload, _convert_api_payload_to_listen
from urllib.parse import urljoin


API_BASE_URL = 'https://api.listenbrainz.org'

class ListenBrainz:


    def set_auth_token(self, auth_token):
        if self.is_token_valid(auth_token):
            self._auth_token = auth_token
        else:
            raise Exception("Invalid Auth token") #TODO


    def require_auth_token(self):
        if not self._auth_token:
            raise Exception("No Auth token") #TODO


    def _get(self, endpoint, params=None, headers=None):
        if not params:
            params = {}
        if not headers:
            headers = {}
        if self._auth_token:
            headers['Authorization'] = 'Token {}'.format(self._auth_token)

        return requests.get(
           urljoin(API_BASE_URL, endpoint),
           params=params,
           headers=headers,
        )


    def _post(self, endpoint, data=None, headers=None):
        if not headers:
            headers = {}
        if self._auth_token:
            headers['Authorization'] = 'Token {}'.format(self._auth_token)
        return requests.post(
           urljoin(API_BASE_URL, endpoint),
           data=data,
           headers=headers,
        )


    def submit_listens(
        self,
        listens,
        listen_type,
    ):
        self.require_auth_token()
        _validate_submit_listens_payload(listen_type, listens)
        listen_payload = [listen.to_submit_payload() for listen in listens]
        submit_json = {
            'listen_type': listen_type,
            'payload': listen_payload
        }

        response = self._post(
            '/1/submit-listens',
            data=json.dumps(submit_json),
        )
        response.raise_for_status() #TODO(param): Raise proper pylistenbrainz exceptions here
        return response.json()


    def is_token_valid(self, token):
        response = self._get(
            '/1/validate-token',
            params={'token': token},
        )
        response.raise_for_status() #TODO(param): Raise proper pylistenbrainz exceptions here
        return response.json()['valid']


    def get_playing_now(self, username):
        response = self._get('/1/{username}/playing-now'.format(username=username))
        response.raise_for_status() #TODO(param): Raise proper pylistenbrainz exceptions here
        data = response.json()
        username = data['payload']['musicbrainz_id']
        listens = data['payload']['listens']
        if len(listens) > 0: # should never be greater than 1
            return _convert_api_payload_to_listen(listens[0], username)
        return None


    def get_listens(self, username, max_ts=None, min_ts=None, count=None):
        params = {}
        if max_ts is not None:
            params['max_ts'] = max_ts
        if min_ts is not None:
            params['min_ts'] = min_ts
        if count is not None:
            params['count'] = count

        response = self._get(
            '/1/{username}/listens'.format(username=username),
            params=params,
        )
        response.raise_for_status() #TODO(param): Raise proper pylistenbrainz exceptions here
        data = response.json()
        username = data['payload']['musicbrainz_id']
        listens = data['payload']['listens']
        return [_convert_api_payload_to_listen(listen_data, username) for listen_data in listens]
