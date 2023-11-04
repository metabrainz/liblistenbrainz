# pylistenbrainz - A simple client library for ListenBrainz
# Copyright (C) 2022 Sam Thursfield <sam@afuera.me.uk>
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


import datetime
import pathlib
import urllib.parse


PLAYLIST_QUERY_TYPE_CREATED_BY = 'created_by'
PLAYLIST_QUERY_TYPE_COLLABORATOR = 'collaborator'
PLAYLIST_QUERY_TYPE_CREATED_FOR = 'created_for'

PLAYLIST_QUERY_TYPES = (
    PLAYLIST_QUERY_TYPE_CREATED_BY,
    PLAYLIST_QUERY_TYPE_COLLABORATOR,
    PLAYLIST_QUERY_TYPE_CREATED_FOR,
)


def _url_to_mbid(url, kind):
    parsed = urllib.parse.urlsplit(url)
    path = pathlib.Path(parsed.path)
    if path.parent.name == kind:
        return path.name
    else:
        raise ValueError("Expected {} URL, got: {}".format(kind, url))


def _mbid_to_url(mbid, kind):
    if kind == 'playlist':
        base = 'https://listenbrainz.org/'
    else:
        base = 'https://musicbrainz.org/'
    path = pathlib.Path(kind).joinpath(mbid)
    return urllib.parse.urljoin(base, str(path))


class PlaylistMetadata():
    """Metadata about a ListenBrainz playlist.

    :param identifier: MBID of the playlist
    :type identifier: str
    :param annotation: A string describing the playlist.
    :type annotation: str, optional
    :param creator: The username of the creator of the playlist.
    :type creator: str, optional
    :param title: The title of the playlist.
    :type title: str, optional
    :param algorithm_metadata: Metadata specific to playlist generator, if any.
    :type algorithm_metadata: dict, optional
    :param collaborators: List of users who have added tracks to the playlist.
    :type collaborators: List[str], optional
    :param last_modified_at: The date the playlist was last modified.
    :type last_modified_at: datetime.datetime, optional
    :param public: Whether the playlist is publicly visible.
    :type public: bool

    """
    def __init__(self,
                 identifier,
                 annotation=None,
                 creator=None,
                 date=None,
                 title=None,
                 algorithm_metadata=None,
                 collaborators=None,
                 last_modified_at=None,
                 public=True):
        self.identifier = identifier
        self.annotation = annotation
        self.creator = creator
        self.date = date
        self.title = title
        self.algorithm_metadata = algorithm_metadata
        self.collaborators = collaborators or []
        self.last_modified_at = last_modified_at
        self.public = public

        self.url = _mbid_to_url(identifier, 'playlist')

    def __repr__(self):
        return('<pylistenbrainz.PlaylistMetadata url="{}">'.format(self.url))

    def identifier(self):
        """The MBID of the playlist."""
        return self.identifier

    def url(self):
        """A URL where the playlist can be found."""
        return self.url


def _maybe_add(data, key, value):
    if key:
        data[key] = value


class PlaylistTrack():
    """A single item in a Listenbrainz playlist.

    :param identifier: the MBID of the recording
    :type identifier: str
    :param creator: the username of the playlist's creator
    :type creator: str
    :param title: the title of the playlist
    :type title: str
    :param added_at: the timestamp when the track was added to the playlist
    :type added_at: datetime.datetime, optional
    :param added_by: the username of the user who added this track
    :type added_by: str, optional
    :param artist_identifiers: the MBID of the recording artist(s)
    :type artist_identifiers: List[str], optional
    """
    def __init__(self,
                 identifier,
                 creator,
                 title,
                 added_at=None,
                 added_by=None,
                 artist_identifiers=None):
        self.identifier = identifier
        self.creator = creator
        self.title = title
        self.added_at = added_at
        self.added_by = added_by
        self.artist_identifiers = artist_identifiers

        self.url = _mbid_to_url(identifier, 'recording')

    def __repr__(self):
        return('<pylistenbrainz.PlaylistTrack url="{}">'.format(self.url))

    def identifier(self):
        """The MBID of the recording."""
        return self.identifier

    def url(self):
        """A URL where the recording can be found."""
        return self.url

    def to_jspf(self):
        """Return the playlist entry as a fragment of JSPF data."""
        ext = {}
        if self.added_at:
            ext['added_at'] = self.added_at.isoformat()
        _maybe_add(ext, 'added_by', self.added_by)
        _maybe_add(ext, 'artist_identifiers', self.artist_identifiers)

        data = {
            'identifier': self.identifier,
            'extension': {
                'https://musicbrainz.org/doc/jspf#track': ext
            },
        }

        _maybe_add(data, 'creator', self.creator)
        _maybe_add(data, 'title', self.title)

        return data


class Playlist():
    """ A ListenBrainz playlist.

    :param metadata: a :class:`PlaylistMetadata` instance.
    :type metadata: PlaylistMetadata

    :param tracks: a list of :class:`PlaylistTrack` instances.
    :type tracks: List[PlaylistTrack]
    """
    def __init__(self, metadata, tracks):
        self.metadata = metadata
        self.tracks = tracks

        self.identifier = metadata.identifier
        self.url = metadata.url

    def __repr__(self):
        return '<pylistenbrainz.Playlist url="{}">'.format(self.url)

    def identifier(self):
        """The MBID of the playlist."""
        return self.identifier

    def url(self):
        """A URL where the playlist can be found."""
        return self.url

    def to_jspf(self):
        """Return the playlist as JSPF data.

        `JSPF <https://xspf.org/jspf>`_ is a variant of the standard
        format `XSPF <https://xspf.org/>`_. ListenBrainz defines some
        extensions to the format which are documented
        `here <https://musicbrainz.org/doc/jspf>`_.

        """
        ext = {}
        _maybe_add(ext, 'algorithm_metadata', self.metadata.algorithm_metadata)
        _maybe_add(ext, 'collaborators', self.metadata.collaborators)
        _maybe_add(ext, 'last_modified_at', self.metadata.last_modified_at.isoformat())
        _maybe_add(ext, 'public', self.metadata.public)

        data = {
            'identifier': self.identifier,
            'extension': {
                'https://musicbrainz.org/doc/jspf#playlist': ext
            },
            'track': [track.to_jspf() for track in self.tracks],
        }
        _maybe_add(data, 'annotation', self.metadata.annotation)
        _maybe_add(data, 'creator', self.metadata.creator)
        _maybe_add(data, 'date', self.metadata.date.isoformat())
        _maybe_add(data, 'title', self.metadata.title)

        return {
            'playlist': data
        }


def _playlist_metadata_from_response(payload):
    data = payload['playlist']
    ext = data['extension']['https://musicbrainz.org/doc/jspf#playlist']
    return PlaylistMetadata(
        identifier = _url_to_mbid(data['identifier'], kind='playlist'),
        annotation = data['annotation'],
        creator = data['creator'],
        date = datetime.datetime.fromisoformat(data['date']),
        title = data['title'],
        algorithm_metadata = ext.get('algorithm_metadata'),
        collaborators = ext['collaborators'],
        last_modified_at = datetime.datetime.fromisoformat(
            ext['last_modified_at']
        ),
        public = ext['public']
    )


def _playlist_from_response(payload):
    metadata = _playlist_metadata_from_response(payload)
    tracks = []
    for track in payload['playlist']['track']:
        ext = track['extension']['https://musicbrainz.org/doc/jspf#track']

        # This property changed name. Support options for now.
        # See https://tickets.metabrainz.org/browse/LB-1058
        ext_artist_identifiers = ext.get(
            'artist_identifiers',
            ext.get(
                'artist_identifier',
                []
            )
        )

        artist_identifiers = [
            _url_to_mbid(artist, kind='artist')
            for artist in ext_artist_identifiers
        ]
        tracks.append(PlaylistTrack(
            identifier = _url_to_mbid(track['identifier'], kind='recording'),
            creator = track['creator'],
            title = track['title'],
            added_at = datetime.datetime.fromisoformat(ext['added_at']),
            added_by = ext['added_by'],
            artist_identifiers = artist_identifiers,
        ))
    return Playlist(metadata, tracks)
