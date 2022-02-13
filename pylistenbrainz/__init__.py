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

__version__ = '0.5.0'

from pylistenbrainz.client import ListenBrainz
from pylistenbrainz.listen import Listen
from pylistenbrainz.listen import LISTEN_TYPE_IMPORT, LISTEN_TYPE_PLAYING_NOW, LISTEN_TYPE_SINGLE
from pylistenbrainz.playlist import Playlist, PlaylistMetadata, PlaylistTrack
from pylistenbrainz.playlist import PLAYLIST_QUERY_TYPE_CREATED_BY, PLAYLIST_QUERY_TYPE_COLLABORATOR, PLAYLIST_QUERY_TYPE_CREATED_FOR
