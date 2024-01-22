
API Reference
=============

ListenBrainz client
####################

The ``ListenBrainz`` class is the main interface provided by liblistenbrainz. It can be used
to interact with the ListenBrainz API.

.. automodule:: liblistenbrainz.client
    :members:
    :undoc-members:
    :show-inheritance:

class Listen
############

The ``Listen`` class  represents a Listen from ListenBrainz.

.. autoclass:: liblistenbrainz.Listen
    :members:
    :special-members: __init__
    :undoc-members:
    :show-inheritance:

Statistics (beta)
#################

ListenBrainz has started exposing statistics endpoints. The following classes are related to
those endpoints.

.. autoclass:: liblistenbrainz.user_artist_stat_response.StatsTimeRangeOptions
.. autoclass:: liblistenbrainz.user_artist_stat_response.UserArtistStatResponse
    :members:
    :special-members: __init__
.. autoclass:: liblistenbrainz.user_artist_stat_response.UserArtistStatRecord
