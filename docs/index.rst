liblistenbrainz Documentation
==========================================

*liblistenbrainz* is a simple Python library for the
`ListenBrainz Web API <https://listenbrainz.readthedocs.io/en/production/dev/api/>`_.
liblistenbrainz should help you start getting data from and submitting data to
`ListenBrainz <https://listenbrainz.org>`_ very quickly.

Here's an example of getting the listening history of a ListenBrainz user::

    import liblistenbrainz

    client = liblistenbrainz.ListenBrainz()
    listens = client.get_listens(username='iliekcomputers')
    for listen in listens:
        print("Track name:", listen.track_name)
        print("Artist name:", listen.artist_name)


Here's another quick example of how to submit a listen to ListenBrainz::

    import liblistenbrainz
    import time

    auth_token = input('Please enter your auth token: ')

    listen = liblistenbrainz.Listen(
        track_name="Fade",
        artist_name="Kanye West",
        release_name="The Life of Pablo",
        listened_at=int(time.time()),
    )

    client = liblistenbrainz.ListenBrainz()
    client.set_auth_token(auth_token)
    response = client.submit_single_listen(listen)

Features
########

liblistenbrainz provides easy access to all ListenBrainz endpoints, handles
ratelimits automatically and supports the ListenBrainz authorization flow.

For details on the API endpoints that can be used via liblistenbrainz, take
a look at the `ListenBrainz API Documentation <https://listenbrainz.readthedocs.io/en/production/dev/api/>`_.

Installation
############

Install or upgrade liblistenbrainz with::

    pip install liblistenbrainz --upgrade

Or you can get the source code from GitHub at https://github.com/paramsingh/liblistenbrainz.


Getting Started
###############

It is easy to get started retrieving data from ListenBrainz using liblistenbrainz. No
authentication is required for getting data.

To submit data for a user, liblistenbrainz requires that you have the user's ListenBrainz auth
token. Each user has a unique auth token available on their profile page.

You can optionally set an auth token for requests to get data as well.

Here's an example of setting an auth token to a liblistenbrainz client::

    import liblistenbrainz

    auth_token = input('Please enter your auth token: ')
    client = liblistenbrainz.ListenBrainz()
    liblistenbrainz.set_auth_token(auth_token)

By default, the ``set_auth_token`` method checks for the validity of the auth token by
making a request to the ListenBrainz API. You can skip this check using the ``check_validity``
param. For example::

    import liblistenbrainz

    auth_token = input('Please enter your auth token: ')
    client = liblistenbrainz.ListenBrainz()
    liblistenbrainz.set_auth_token(auth_token, check_validity=False)

Examples
########

There are more examples of how to use liblistenbrainz
in the `examples directory on GitHub <https://github.com/paramsingh/liblistenbrainz/tree/master/examples>`_.

API Reference
#############

There are more details about the client interface on the :doc:`API reference page <api_ref>`.

Exceptions
##########

All exceptions raised by liblistenbrainz should inherit
from the base class ``liblistenbrainz.errors.ListenBrainzException``.

For a comprehensive list of exceptions that the library can raise,
take a look at the :doc:`exceptions page <exceptions>`.

Support
#######

You can ask questions about how to use liblistenbrainz on IRC (freenode #metabrainz).
You can also email me at ``iliekcomputers [at] gmail [dot] com``.

If you have found a bug or have a feature request,
let me know by opening a `GitHub Issue <https://github.com/paramsingh/liblistenbrainz/issues>`_.

License
#######

https://github.com/paramsingh/liblistenbrainz/blob/master/LICENSE


Table Of Contents
#################

.. toctree::
    :maxdepth: 2

    api_ref
    exceptions

Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
