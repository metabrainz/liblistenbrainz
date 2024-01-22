# liblistenbrainz

*liblistenbrainz* is a simple Python library for the
[ListenBrainz Web API](https://listenbrainz.readthedocs.io/en/production/dev/api/).

liblistenbrainz will help you start getting data from and submitting data to
[ListenBrainz](https://listenbrainz.org>) very quickly.

Here's an example of getting the listening history of a ListenBrainz user::

``` python
import liblistenbrainz

client = liblistenbrainz.ListenBrainz()
listens = client.get_listens(username='iliekcomputers')
for listen in listens:
    print("Track name:", listen.track_name)
    print("Artist name:", listen.artist_name)
```

Here's another quick example of how to submit a listen to ListenBrainz::

``` python
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
```

More detailed documentation is available
at [Read The Docs](https://liblistenbrainz.readthedocs.io/en/latest/).

## Features

liblistenbrainz provides easy access to all ListenBrainz endpoints, handles
ratelimits automatically and supports the ListenBrainz authorization flow.

For details on the API endpoints that can be used via liblistenbrainz, take
a look at the [ListenBrainz API Documentation](https://listenbrainz.readthedocs.io/en/production/dev/api/).

## Installation

Install or upgrade liblistenbrainz with:

    pip install liblistenbrainz --upgrade

## Support

You can ask questions about how to use liblistenbrainz on IRC (freenode #metabrainz).
You can also email me at `iliekcomputers [at] gmail [dot] com`.

If you have found a bug or have a feature request, let me know by opening an issue (or a pull request).

## License

```
liblistenbrainz - A simple client library for ListenBrainz
Copyright (C) 2020 Param Singh <iliekcomputers@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
