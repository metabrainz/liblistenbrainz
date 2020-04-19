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
import time

from pylistenbrainz import errors
from pylistenbrainz.listen import LISTEN_TYPE_IMPORT, LISTEN_TYPE_PLAYING_NOW, LISTEN_TYPE_SINGLE
from pylistenbrainz.utils import _validate_submit_listens_payload, _convert_api_payload_to_listen
from urllib.parse import urljoin


API_BASE_URL = 'https://api.listenbrainz.org'

class ListenBrainz:

    def __init__(self):
        self._auth_token = None

        # initialize rate limit variables with None
        self._last_request_ts = None
        self.remaining_requests = None
        self.ratelimit_reset_in = None


    def _require_auth_token(self):
        if not self._auth_token:
            raise errors.AuthTokenRequiredException


    def _wait_until_rate_limit(self):
        # if we haven't made any request before this, return
        if self._last_request_ts is None:
            return

        # if we have available requests in this window, return
        if self.remaining_requests and self.remaining_requests > 0:
            return

        # if we don't have available requests and we know when the
        # window is reset, backoff until the window gets reset
        if self.ratelimit_reset_in is not None:
            reset_ts = self._last_request_ts + self.ratelimit_reset_in
            current_ts = int(time.time())
            if current_ts < reset_ts:
                time.sleep(reset_ts - current_ts)


    def _update_rate_limit_variables(self, response):
        self._last_request_ts = int(time.time())
        try:
            self.remaining_requests = int(response.headers.get('X-RateLimit-Remaining'))
        except (TypeError, ValueError):
            self.remaining_requests = None

        try:
            self.ratelimit_reset_in = int(response.headers.get('X-RateLimit-Reset-In'))
        except (TypeError, ValueError):
            self.ratelimit_reset_in = None


    def _get(self, endpoint, params=None, headers=None):
        if not params:
            params = {}
        if not headers:
            headers = {}
        if self._auth_token:
            headers['Authorization'] = 'Token {}'.format(self._auth_token)

        try:
            self._wait_until_rate_limit()
            response = requests.get(
                urljoin(API_BASE_URL, endpoint),
                params=params,
                headers=headers,
            )
            self._update_rate_limit_variables(response)
            response.raise_for_status()
        except requests.HTTPError as e:
            status_code = e.response.status_code

            # get message from the json in the response if possible
            try:
                message = e.response.json().get('error', '')
            except Exception:
                message = None
            raise errors.ListenBrainzAPIException(
                status_code=status_code,
                message=message
            )
        return response.json()


    def _post(self, endpoint, data=None, headers=None):
        if not headers:
            headers = {}
        if self._auth_token:
            headers['Authorization'] = 'Token {}'.format(self._auth_token)
        try:
            self._wait_until_rate_limit()
            response = requests.post(
                urljoin(API_BASE_URL, endpoint),
                data=data,
                headers=headers,
            )
            self._update_rate_limit_variables(response)
            response.raise_for_status()
        except requests.HTTPError as e:
            status_code = e.response.status_code

            # get message from the json in the response if possible
            try:
                message = e.response.json().get('error', '')
            except Exception:
                message = None
            raise errors.ListenBrainzAPIException(
                status_code=status_code,
                message=message
            )
        return response.json()


    def _post_submit_listens(self, listens, listen_type):
        self._require_auth_token()
        _validate_submit_listens_payload(listen_type, listens)
        listen_payload = [listen._to_submit_payload() for listen in listens]
        submit_json = {
            'listen_type': listen_type,
            'payload': listen_payload
        }
        return self._post(
            '/1/submit-listens',
            data=json.dumps(submit_json),
        )


    def set_auth_token(self, auth_token, check_validity=True):
        """
        Give the client an auth_token to use for future requests.
        This is required if the client wishes to submit listens. Each user
        has a unique auth token and the auth token is used to identify the user
        whose data is being submitted.

        :param auth_token: auth token
        :type auth_token: str
        :param check_validity: specify whether we should check the validity
            of the auth token by making a request to ListenBrainz before setting it (defaults to True)
        :type check_validity: bool, optional
        :raises InvalidAuthTokenException: if ListenBrainz tells us that the token is invalid
        :raises ListenBrainzAPIException: if there is an error with the validity check API call
        """
        if not check_validity or self.is_token_valid(auth_token):
            self._auth_token = auth_token
        else:
            raise errors.InvalidAuthTokenException


    def submit_multiple_listens(self, listens):
        """ Submit a list of listens to ListenBrainz.

        Requires that the auth token for the user whose listens are being submitted has been set.

        :param listens: the list of listens to be submitted
        :type listens: List[pylistenbrainz.Listen]
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        :raises InvalidSubmitListensPayloadException: if the listens sent are invalid, see exception message for details
        """
        return self._post_submit_listens(listens, LISTEN_TYPE_IMPORT)


    def submit_single_listen(self, listen):
        """ Submit a single listen to ListenBrainz.

        Requires that the auth token for the user whose data is being submitted has been set.

        :param listen: the listen to be submitted
        :type listen: pylistenbrainz.Listen
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        :raises InvalidSubmitListensPayloadException: if the listen being sent is invalid, see exception message for details
        """
        return self._post_submit_listens([listen], LISTEN_TYPE_SINGLE)


    def submit_playing_now(self, listen):
        """ Submit a playing now notification to ListenBrainz.

        Requires that the auth token for the user whose data is being submitted has been set.

        :param listen: the listen to be submitted, the listen should NOT have a `listened_at` attribute
        :type listen: pylistenbrainz.Listen
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        :raises InvalidSubmitListensPayloadException: if the listen being sent is invalid, see exception message for details
        """
        return self._post_submit_listens([listen], LISTEN_TYPE_PLAYING_NOW)


    def is_token_valid(self, token):
        """ Check if the specified ListenBrainz auth token is valid using the ``/1/validate-token`` endpoint.

        :param token: the auth token that needs to be checked for validity
        :type token: str
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        """
        data = self._get(
            '/1/validate-token',
            params={'token': token},
        )
        return data['valid']


    def get_playing_now(self, username):
        """ Get the listen being played right now for user `username`.

        :param username: the username of the user whose data is to be fetched
        :type username: str
        :return: A single listen if the user is playing something currently, else None
        :rtype: `pylistenbrainz.Listen` or `None`
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        """
        data = self._get('/1/user/{username}/playing-now'.format(username=username))
        listens = data['payload']['listens']
        if len(listens) > 0: # should never be greater than 1
            return _convert_api_payload_to_listen(listens[0])
        return None


    def get_listens(self, username, max_ts=None, min_ts=None, count=None):
        """ Get listens for user `username`

        If none of the optional arguments are given, this endpoint will return the 25 most recent listens.
        The optional `max_ts` and `min_ts` UNIX epoch timestamps control at which point in time to start returning listens.
        You may specify max_ts or min_ts, but not both in one call.

        :param username: the username of the user whose data is to be fetched
        :type username: str
        :param max_ts: If you specify a max_ts timestamp, listens with listened_at less than (but not including) this value will be returned.
        :type max_ts: int, optional
        :param min_ts: If you specify a min_ts timestamp, listens with listened_at greater than (but not including) this value will be returned.
        :type min_ts: int, optional
        :param count: the number of listens to return. Defaults to 25, maximum is 100.
        :type count: int, optional
        :return: A list of listens for the user `username`
        :rtype: Listen[pylistenbrainz.Listen]
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        """
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
