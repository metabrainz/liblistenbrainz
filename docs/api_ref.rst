
API Reference
=============

ListenBrainz client
####################

The ``ListenBrainz`` class is the main interface provided by pylistenbrainz. It can be used
to interact with the ListenBrainz API.

.. automodule:: pylistenbrainz.client
    :members:
    :undoc-members:
    :show-inheritance:

class Listen
############

The ``Listen`` class  represents a Listen from ListenBrainz.

.. autoclass:: pylistenbrainz.Listen
    :members:
    :special-members: __init__
    :undoc-members:
    :show-inheritance:

Playlists module
################

The following classes represent ListenBrainz playlists.

class Playlist
~~~~~~~~~~~~~~

.. autoclass:: pylistenbrainz.Playlist
    :members:
    :undoc-members:

class PlaylistMetadata
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: pylistenbrainz.PlaylistMetadata
    :members:
    :undoc-members:

class PlaylistTrack
~~~~~~~~~~~~~~~~~~~

.. autoclass:: pylistenbrainz.PlaylistTrack
    :members:
    :undoc-members:

Statistics (beta)
#################

ListenBrainz has started exposing statistics endpoints. The following classes are related to
those endpoints.

.. autoclass:: pylistenbrainz.user_artist_stat_response.StatsTimeRangeOptions
.. autoclass:: pylistenbrainz.user_artist_stat_response.UserArtistStatResponse
    :members:
    :special-members: __init__
.. autoclass:: pylistenbrainz.user_artist_stat_response.UserArtistStatRecord
