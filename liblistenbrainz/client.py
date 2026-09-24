# liblistenbrainz - A simple client library for ListenBrainz
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
from requests.adapters import HTTPAdapter
import time
from urllib3.util import Retry

from liblistenbrainz import __version__, errors
from liblistenbrainz.listen import LISTEN_TYPE_IMPORT, LISTEN_TYPE_PLAYING_NOW, LISTEN_TYPE_SINGLE
from liblistenbrainz.utils import _validate_submit_listens_payload, _convert_api_payload_to_listen

retry_strategy = Retry(total=5, allowed_methods=('GET', 'POST'), status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)

STATS_SUPPORTED_TIME_RANGES = (
    'week',
    'month',
    'quarter',
    'half_yearly',
    'year',
    'all_time',
    'this_week',
    'this_month',
    'this_year'
)




class ListenBrainz:

    def __init__(self, api_base_url = 'https://api.listenbrainz.org'):
        self._auth_token = None

        # initialize rate limit variables with None
        self._last_request_ts = None
        self.remaining_requests = None
        self.ratelimit_reset_in = None
        self.api_base_url = api_base_url


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


    def _build_url(self, endpoint):
        return f"{self.api_base_url.rstrip('/')}/{endpoint.lstrip('/')}"


    def _get(self, endpoint, params=None, headers=None, destination=None):
        if not params:
            params = {}
        if not headers:
            headers = {}
        if self._auth_token:
            headers['Authorization'] = f'Token {self._auth_token}'

        with requests.Session() as session:
            session.headers['User-Agent'] = f'liblistenbrainz/{__version__}'
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            request_options = {'stream': True} if destination is not None else {}

            self._wait_until_rate_limit()
            with session.get(
                self._build_url(endpoint),
                params=params,
                headers=headers,
                **request_options,
            ) as response:
                self._update_rate_limit_variables(response)
                try:
                    response.raise_for_status()
                except requests.HTTPError as e:
                    status_code = e.response.status_code

                    # get message from the json in the response if possible
                    try:
                        message = e.response.json().get('error', '')
                    except Exception:
                        message = None
                    raise errors.ListenBrainzAPIException(status_code=status_code, message=message) from e

                if response.status_code == 204:
                    raise errors.ListenBrainzAPIException(status_code=204)
                if destination is not None:
                    with open(destination, 'wb') as output:
                        for chunk in response.iter_content(chunk_size=64 * 1024):
                            if chunk:
                                output.write(chunk)
                    return destination
                return response.json()


    def _post(self, endpoint, data=None, headers=None, retry=True):
        if not headers:
            headers = {}
        if self._auth_token:
            headers['Authorization'] = f'Token {self._auth_token}'

        session = requests.Session()
        session.headers['User-Agent'] = f'liblistenbrainz/{__version__}'
        if retry:
            session.mount("http://", adapter) # http is not used, but in case someone needs to use to for dev work, its included here
            session.mount("https://", adapter)

        try:
            self._wait_until_rate_limit()
            response = session.post(
                self._build_url(endpoint),
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
            raise errors.ListenBrainzAPIException(status_code=status_code, message=message) from e

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
        self._auth_token = auth_token
        if check_validity:
            response = self._get("/1/validate-token")
            if not response["valid"]:
                raise errors.InvalidAuthTokenException


    def submit_multiple_listens(self, listens):
        """ Submit a list of listens to ListenBrainz.

        Requires that the auth token for the user whose listens are being submitted has been set.

        :param listens: the list of listens to be submitted
        :type listens: List[liblistenbrainz.Listen]
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        :raises InvalidSubmitListensPayloadException: if the listens sent are invalid, see exception message for details
        """
        return self._post_submit_listens(listens, LISTEN_TYPE_IMPORT)


    def submit_single_listen(self, listen):
        """ Submit a single listen to ListenBrainz.

        Requires that the auth token for the user whose data is being submitted has been set.

        :param listen: the listen to be submitted
        :type listen: liblistenbrainz.Listen
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        :raises InvalidSubmitListensPayloadException: if the listen being sent is invalid, see exception message for details
        """
        return self._post_submit_listens([listen], LISTEN_TYPE_SINGLE)


    def submit_playing_now(self, listen):
        """ Submit a playing now notification to ListenBrainz.

        Requires that the auth token for the user whose data is being submitted has been set.

        :param listen: the listen to be submitted, the listen should NOT have a `listened_at` attribute
        :type listen: liblistenbrainz.Listen
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        :raises InvalidSubmitListensPayloadException: if the listen being sent is invalid, see exception message for details
        """
        return self._post_submit_listens([listen], LISTEN_TYPE_PLAYING_NOW)

    def submit_user_feedback(self, feedback, recording_mbid):
        """ Submit a feedback to Listenbrainz
            
        Requires that the auth token for the user whose data is being submitted has been set.

        :param feedback The type of feedback 1 = loved, -1 = hated, 0 = delete feedback if any
        :param recording_mbid The recording Musicbrainz Id of the track being anotated
        """
        data = {
            'score': feedback,
            'recording_mbid': recording_mbid,
        }
        headers = {
            'Content-Type': 'application/json',
        }
        return self._post(
            '/1/feedback/recording-feedback',
            data=json.dumps(data),
            headers=headers,
        )


    def delete_listen(self, listen):
        """ Delete a particular listen from a user’s listen history.

        The listen is not deleted immediately, but is scheduled for deletion, which usually happens shortly after the hour.

        Requires that the auth token for the user whose data is being submitted has been set.

        :param listen: the listen to be deleted. The listen must have a `listened_at` and `recording_msid` attribute
        :type listen: liblistenbrainz.Listen
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        :raises InvalidSubmitListensPayloadException: if the listen being sent is invalid, see exception message for details
        """
        data = {
            'listened_at': listen.listened_at,
            'recording_msid': listen.recording_msid,
        }
        headers = {
            'Content-Type': 'application/json',
        }
        return self._post(
            '/1/delete-listen',
            data=json.dumps(data),
            headers=headers,
        )


    def create_export(self, start_time=None, end_time=None):
        """ Queue an export for the authenticated user.

        Omit both bounds to export the full listening history. Bounds are inclusive
        UNIX timestamps in seconds and filter listens only; feedback, pinned
        recordings, and account information are always exported in full.
        Only one export may be pending per user. This method does not poll or
        automatically retry: after a timeout, call :meth:`list_exports` before
        trying again, as the first request may already have queued an export.

        :param start_time: inclusive start of the listen range, or None to omit
        :type start_time: int, optional
        :param end_time: inclusive end of the listen range, or None to omit
        :type end_time: int, optional
        :return: export metadata, including export_id and status
        :rtype: dict
        :raises AuthTokenRequiredException: if no auth token has been set
        :raises ValueError: if bounds are not integers or start_time exceeds end_time
        :raises ListenBrainzAPIException: if the API rejects the request
        """
        self._require_auth_token()
        bounds = {}
        for name, value in (('start_time', start_time), ('end_time', end_time)):
            if value is not None:
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError(f'{name} must be an integer UNIX timestamp')
                bounds[name] = value
        if start_time is not None and end_time is not None and start_time > end_time:
            raise ValueError('start_time must be less than or equal to end_time')
        return self._post(
            '/1/export/',
            data=json.dumps(bounds) if bounds else None,
            headers={'Content-Type': 'application/json'} if bounds else None,
            retry=False,
        )


    def list_exports(self):
        """ List the authenticated user's exports, newest first.

        Reuse a suitable completed export or poll an existing pending export
        before creating another. There are no pagination parameters.

        :return: export metadata objects, or an empty list if there are none
        :rtype: list[dict]
        :raises AuthTokenRequiredException: if no auth token has been set
        :raises ListenBrainzAPIException: if the API rejects the request
        """
        self._require_auth_token()
        return self._get('/1/export/list')


    def get_export(self, export_id):
        """ Get an export's metadata for the authenticated user.

        Status is waiting, in_progress, completed, or failed. Poll at intervals
        of at least 30 seconds, increasing the delay with jitter up to around
        120 seconds. Stop polling on failure. Use available_until to determine
        when a completed archive expires.

        :param export_id: the ID returned by create_export or list_exports
        :type export_id: int
        :return: export metadata, including status and progress
        :rtype: dict
        :raises AuthTokenRequiredException: if no auth token has been set
        :raises ListenBrainzAPIException: if the API rejects the request
        """
        self._require_auth_token()
        return self._get(f'/1/export/{export_id}')


    def download_export(self, export_id, destination):
        """ Stream a completed export's ZIP archive to a local file.

        The destination is overwritten once the server accepts the request.
        An interrupted download may leave a partial file; restart with the same
        export ID. Downloads cannot be resumed. A 404 may mean the export is
        unfinished or expired; check its status before requesting a new one.

        :param export_id: the ID of the completed export
        :type export_id: int
        :param destination: local path at which to save the archive
        :type destination: str or os.PathLike
        :return: the destination path
        :rtype: str or os.PathLike
        :raises AuthTokenRequiredException: if no auth token has been set
        :raises ListenBrainzAPIException: if the API rejects the request
        :raises OSError: if the destination cannot be written
        """
        self._require_auth_token()
        return self._get(f'/1/export/{export_id}/download', destination=destination)


    def delete_export(self, export_id):
        """ Delete an export record and its queued task for the authenticated user.

        Archive storage is reclaimed asynchronously and a running worker may
        not stop immediately. Exports are shared by the user's clients, so only
        delete an export when it is no longer needed by any of them.

        :param export_id: the ID of the export to delete
        :type export_id: int
        :return: the API response, containing success on successful deletion
        :rtype: dict
        :raises AuthTokenRequiredException: if no auth token has been set
        :raises ListenBrainzAPIException: if the API rejects the request
        """
        self._require_auth_token()
        return self._post(f'/1/export/{export_id}/delete')


    def get_playing_now(self, username):
        """ Get the listen being played right now for user `username`.

        :param username: the username of the user whose data is to be fetched
        :type username: str
        :return: A single listen if the user is playing something currently, else None
        :rtype: liblistenbrainz.Listen or None
        :raises ListenBrainzAPIException: if the ListenBrainz API returns a non 2xx return code
        """
        data = self._get('/1/user/{username}/playing-now'.format(username=username))
        listens = data['payload']['listens']
        if len(listens) > 0: # should never be greater than 1
            return _convert_api_payload_to_listen(listens[0])
        return None


    def get_listens(self, username, max_ts=None, min_ts=None, count=None):
        """ Get listens for user `username`

        If none of the optional arguments are given, this function will return the 25 most recent listens.
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
        :rtype: List[liblistenbrainz.Listen]
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

    def _get_user_entity(self, username, entity, count=25, offset=0, time_range='all_time'):
        if time_range not in STATS_SUPPORTED_TIME_RANGES:
            raise errors.ListenBrainzException(f"Invalid time range: {time_range}")

        params = {
            'count': count,
            'offset': offset,
            'range': time_range,
        }

        try:
            return self._get(f'/1/stats/user/{username}/{entity}', params=params)
        except errors.ListenBrainzAPIException as e:
            if e.status_code == 204:
                return None
            else:
                raise


    def get_user_artists(self, username, count=25, offset=0, time_range='all_time'):
        """ Get artists for user 'username', sorted in descending order of listen count.

        :param username: the username of the user whose artists are to be fetched.
        :type username: str

        :param count: the number of artists to fetch, defaults to 25, maximum is 100.
        :type count: int, optional

        :param offset: the number of artists to skip from the beginning, for pagination, defaults to 0.
        :type offset: int, optional

        :param time_range: the time range, can be 'week', 'month', 'quarter', 'half_yearly', 'year', 'this_week', 'this_month', 'this_year' or 'all_time'.
        :type time_range: str

        :return: the artists listened to by the user in the time range with listen counts and other data in the same format as the API response
        :rtype: dict
        """
        return self._get_user_entity(username, 'artists', count, offset, time_range)


    def get_user_recordings(self, username, count=25, offset=0, time_range='all_time'):
        """ Get recordings for user 'username', sorted in descending order of listen count.

        :param username: the username of the user whose artists are to be fetched.
        :type username: str

        :param count: the number of recordings to fetch, defaults to 25, maximum is 100.
        :type count: int, optional

        :param offset: the number of recordings to skip from the beginning, for pagination, defaults to 0.
        :type offset: int, optional

        :param time_range: the time range, can be 'week', 'month', 'quarter', 'half_yearly', 'year', 'this_week', 'this_month', 'this_year' or 'all_time'.
        :type time_range: str

        :return: the recordings listened to by the user in the time range with listen counts and other data, in the same format as the API response
        :rtype: dict
        """
        return self._get_user_entity(username, 'recordings', count, offset, time_range)


    def get_user_releases(self, username, count=25, offset=0, time_range='all_time'):
        """ Get releases for user 'username', sorted in descending order of listen count.

        :param username: the username of the user whose releases are to be fetched.
        :type username: str

        :param count: the number of releases to fetch, defaults to 25, maximum is 100.
        :type count: int, optional

        :param offset: the number of releases to skip from the beginning, for pagination, defaults to 0.
        :type offset: int, optional

        :param time_range: the time range, can be 'week', 'month', 'quarter', 'half_yearly', 'year', 'this_week', 'this_month', 'this_year' or 'all_time'.
        :type time_range: str

        :return: the releases listened to by the user in the time range with listen counts and other data
        :rtype: dict
        """
        return self._get_user_entity(username, 'releases', count, offset, time_range)

    def get_user_release_groups(self, username, count=25, offset=0, time_range='all_time'):
        """ Get release groups for user 'username', sorted in descending order of listen count.

        :param username: the username of the user whose release groups are to be fetched.
        :type username: str

        :param count: the number of release groups to fetch, defaults to 25, maximum is 100.
        :type count: int, optional

        :param offset: the number of release groups to skip from the beginning, for pagination, defaults to 0.
        :type offset: int, optional

        :param time_range: the time range, can be 'week', 'month', 'quarter', 'half_yearly', 'year', 'this_week', 'this_month', 'this_year' or 'all_time'.
        :type time_range: str

        :return: the release groups listened to by the user in the time range with listen counts and other data
        :rtype: dict
        """
        return self._get_user_entity(username, 'release-groups', count, offset, time_range)


    def get_user_recommendation_recordings(self, username, artist_type='top', count=25, offset=0):
        """ Get recommended recordings for a user.

        :param username: the username of the user whose recommended tracks are to be fetched.
        :type username: str

        :param artist_type: The type of filtering applied to the recommended tracks.
                            'top' for filtering by top artists or
                            'similar' for filtering by similar artists
                            'raw' for no filtering
        :type artist_type: str

        :param count: the number of recordings to fetch, defaults to 25, maximum is 100.
        :type count: int, optional

        :param offset: the number of releases to skip from the beginning, for pagination, defaults to 0.
        :type offset: int, optional

        :return: the recommended recordings as other data returned by the API
        :rtype: dict
        """

        if artist_type not in ('top', 'similar', 'raw'):
            raise ValueError("artist_type must be either top or similar or raw.")
        params = {
                    'artist_type': artist_type,
                    'count': count,
                    'offset': offset
                 }
        try:
            return self._get(f'/1/cf/recommendation/user/{username}/recording', params=params)

        except errors.ListenBrainzAPIException as e:
            if e.status_code == 204:
                return None
            else:
                raise

    def get_user_listen_count(self, username):
        """ Get total number of listens for user

        :param username: The username of the user whose listens are to be fetched
        :type username: str

        :return: Number of listens returned by the Listenbrainz API
        :rtype: int
        """
        try:
            return self._get(f'/1/user/{username}/listen-count')['payload']['count']
        except errors.ListenBrainzAPIException as e:
            if e.status_code == 204:
                return None
            else:
                raise

    def get_user_feedback(self, username, score, metadata, count=100, offset=0 ):
        """ Get feedback given by user
        
        :param username: The user to get the feedbacks from
        :type username: str
        :param count: Optional, number of feedback items to return. Default 100.
        :type count: int, optional
        :param offset:  Optional, number of feedback items to skip from the beginning, for pagination. Ex. An offset of 5 means the top 5 feedback will be skipped, defaults to 0.
        :type offset: int, optional
        :param score: Optional, If 1 then returns the loved recordings, if -1 returns hated recordings.
        :type score: int, optional
        :param metadata: Optional, boolean if this call should return the metadata for the feedback.
        :type metadata: bool, optional
        """
        params = {
                    'count': count,
                    'offset': offset,
                    'score': score,
                    'metadata': metadata,
                 }
        try:
            return self._get(f'/1/feedback/user/{username}/get-feedback', params=params)
        except errors.ListenBrainzAPIException as e:
            if e.status_code == 204:
                return None
            else:
                raise
