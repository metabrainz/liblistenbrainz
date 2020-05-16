from typing import List
from enum import Enum

class StatsTimeRangeOptions(Enum):
    """ An enum to list the options for range in the stats endpoint

    Use ``StatsTimeRangeOptions.ALL_TIME`` for 'all_time'.
    """
    ALL_TIME = 'all_time'


class UserArtistStatRecord:
    def __init__(self, listen_count, artist_name, artist_msid, artist_mbids):
        """ Creates a new artist stat record.

        :param listen_count: the number of times the artist was listened to.
        :type listen_count: int

        :param artist_name: the name of the artist
        :type artist_name: str

        :param artist_msid: the MessyBrainz ID of the artist,
        :type artist_msid: str or None

        :param artist_mbids: the MusicBrainz ID(s) of the artist
        :type artist_mbids: List[str]
        """
        self.listen_count = listen_count
        self.artist_name = artist_name
        self.artist_msid = artist_msid
        self.artist_mbids = artist_mbids if artist_mbids else []

class UserArtistStatResponse:
    """ A wrapper class over the ListenBrainz API top artists response.
    """
    def __init__(self, username, total_artist_count, time_range, last_updated, artists):
        """ Creates a new Response object

        :param username: the MusicBrainz ID of the user whose stats were returned
        :type username: str

        :param total_artist_count: the total number of artists the user has listened to
        :type total_artist_count: int

        :param time_range: the time range of the stats returned
        :type time_range: pylistenbrainz.client.StatsTimeRangeOptions

        :param last_updated: the time when the stat was updated by ListenBrainz
        :type last_updated: datetime

        :param artists: the artists the user has listened to, and related data
        :type artists: List[UserArtistStatRecord]
        """
        self.username = username
        self.total_artist_count = total_artist_count
        self.range = time_range
        self.last_updated = last_updated
        self.artists = artists