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

Note that automatic rate limiting is applied to the ``liblistenbrainz.ListenBrainz()``
client; therefore rate limits may be exceeded in cases where multiple clients are 
initialized (resulting in 403 errors from the ListenBrainz Web API).

For details on the API endpoints that can be used via liblistenbrainz, take
a look at the `ListenBrainz API Documentation <https://listenbrainz.readthedocs.io/en/production/dev/api/>`_.

Installation
############

Install or upgrade liblistenbrainz with::

    pip install liblistenbrainz --upgrade

Or you can get the source code from GitHub at https://github.com/paramsingh/liblistenbrainz.


Getting Started
###############

It is easy to get started retrieving public data from ListenBrainz using liblistenbrainz.
User history exports require authentication, including listing and downloading exports.

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

User history exports
####################

Use an export for a large history import and ``get_listens`` for recent listens or
small incremental updates. All export methods use the account identified by the
auth token; they take no username. See the
`export API documentation <https://listenbrainz.readthedocs.io/en/latest/users/api/export.html>`_
for the archive format and server limits.

List existing exports first so you can reuse a suitable completed archive or
resume an existing job::

    import os
    import liblistenbrainz

    client = liblistenbrainz.ListenBrainz()
    client.set_auth_token(os.environ['LB_TOKEN'])
    exports = client.list_exports()

When no suitable export exists, request one and save its ID::

    export = client.create_export()
    export_id = export['export_id']

For a limited listen range, use ``create_export(start_time=1767225600,
end_time=1769903999)`` instead. Both bounds are inclusive integer UNIX timestamps;
either can be omitted with ``None``. Feedback, pinned recordings, and account
information are exported in full regardless of the listen range.

Check the saved ID in a later call::

    export = client.get_export(export_id)
    if export['status'] == 'completed':
        client.download_export(export_id, 'history.zip')

The library does not poll automatically. Space status requests at least 30 seconds
apart and increase the delay with jitter up to around 120 seconds. Stop on
``failed`` and check ``available_until`` before using a completed export.
Creation is not automatically retried: after a timeout, list exports before
requesting another job.

Downloads stream to disk and return the destination path. Existing files are
overwritten; an interruption may leave a partial file. Restart downloads with
the same export ID. A download 404 does not imply that a new export is needed.
When an export is no longer needed by any of the user's clients, explicitly call
``client.delete_export(export_id)``; exports are never deleted automatically.

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
