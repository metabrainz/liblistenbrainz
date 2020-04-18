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

LISTEN_TYPE_SINGLE = 'single'
LISTEN_TYPE_IMPORT = 'import'
LISTEN_TYPE_PLAYING_NOW = 'playing_now'

LISTEN_TYPES = (
    LISTEN_TYPE_SINGLE,
    LISTEN_TYPE_IMPORT,
    LISTEN_TYPE_PLAYING_NOW,
)

class Listen:
    def __init__(
        self,
        track_name,
        artist_name,
        listened_at=None,
        release_name=None,
        recording_mbid=None,
        artist_mbids=None,
        release_mbid=None,
        tags=None,
        release_group_mbids=None,
        work_mbids=None,
        tracknumber=None,
        spotify_id=None,
        listening_from=None,
        isrc=None,
        additional_info=None,
        username=None
    ):
        self.listened_at = listened_at
        self.track_name = track_name
        self.artist_name = artist_name
        self.release_name = release_name
        self.recording_mbid = recording_mbid
        self.artist_mbids = artist_mbids if artist_mbids else []
        self.release_mbid = release_mbid
        self.tags = tags if tags else []
        self.release_group_mbids = release_group_mbids if release_group_mbids else []
        self.work_mbids = work_mbids if work_mbids else []
        self.tracknumber = tracknumber
        self.spotify_id = spotify_id
        self.listening_from = listening_from
        self.isrc = isrc
        self.additional_info = additional_info if additional_info else {}
        self.username = username


    def to_submit_payload(self):
        # create the additional_info dict first
        additional_info = self.additional_info
        if self.recording_mbid:
            additional_info['recording_mbid'] = self.recording_mbid
        if self.artist_mbids:
            additional_info['artist_mbids'] = self.artist_mbids
        if self.release_mbid:
            additional_info['release_mbid'] = self.release_mbid
        if self.tags:
            additional_info['tags'] = self.tags
        if self.release_group_mbids:
            additional_info['release_group_mbids'] = self.release_group_mbids
        if self.work_mbids:
            additional_info['work_mbids'] = self.work_mbids
        if self.tracknumber is not None:
            additional_info['tracknumber'] = self.tracknumber
        if self.spotify_id:
            additional_info['spotify_id'] = self.spotify_id
        if self.listening_from:
            additional_info['listening_from'] = self.listening_from
        if self.isrc:
            additional_info['isrc'] = self.isrc

        # create track_metadata now and put additional_info into it if it makes sense
        track_metadata = {
            'track_name': self.track_name,
            'artist_name': self.artist_name,
        }
        if self.release_name:
            track_metadata['release_name'] = self.release_name
        if additional_info:
            track_metadata['additional_info'] = additional_info

        # create final payload and put track metadata into it
        payload = {
            'track_metadata': track_metadata,
        }
        if self.listened_at is not None:
            payload['listened_at'] = self.listened_at

        return payload
