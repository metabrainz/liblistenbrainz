import liblistenbrainz

auth_token = input('Please enter your auth token: ')

listen = liblistenbrainz.Listen(
    track_name="Fade",
    artist_name="Kanye West",
    release_name="The Life of Pablo",
)

client = liblistenbrainz.ListenBrainz()
client.set_auth_token(auth_token)
response = client.submit_playing_now(listen)
assert response['status'] == 'ok'

