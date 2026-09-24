import io
from unittest import mock
import zipfile

import pytest
import requests

import liblistenbrainz
from liblistenbrainz import errors


@pytest.fixture
def client():
    client = liblistenbrainz.ListenBrainz()
    client.set_auth_token('test-token', check_validity=False)
    return client


@pytest.fixture
def export():
    return {
        'export_id': 123,
        'type': 'export_all_user_data',
        'available_until': None,
        'created': '2026-09-17T12:00:00+00:00',
        'progress': 'Your data export will start soon.',
        'status': 'waiting',
        'filename': None,
        'start_time': None,
        'end_time': None,
    }


@pytest.mark.parametrize('method,args', [
    ('create_export', ()),
    ('list_exports', ()),
    ('get_export', (123,)),
    ('download_export', (123, 'history.zip')),
    ('delete_export', (123,)),
])
def test_exports_require_authentication(requests_mock, method, args):
    with pytest.raises(errors.AuthTokenRequiredException):
        getattr(liblistenbrainz.ListenBrainz(), method)(*args)
    assert not requests_mock.called


@pytest.mark.parametrize('bounds', [
    {},
    {'start_time': 0},
    {'end_time': 1769903999},
    {'start_time': 1767225600, 'end_time': 1769903999},
    {'start_time': 0, 'end_time': 0},
])
def test_create_export(client, export, requests_mock, bounds):
    export.update(bounds)
    requests_mock.post('https://api.listenbrainz.org/1/export/', json=export)

    assert client.create_export(**bounds) == export
    request = requests_mock.last_request
    assert request.headers['Authorization'] == 'Token test-token'
    assert request.headers['User-Agent'].startswith('liblistenbrainz/')
    if bounds:
        assert request.json() == bounds
        assert request.headers['Content-Type'] == 'application/json'
    else:
        assert request.body is None


@pytest.mark.parametrize('bounds', [
    {'start_time': '123'},
    {'end_time': 123.5},
    {'start_time': True},
    {'end_time': False},
    {'start_time': 2, 'end_time': 1},
])
def test_invalid_export_bounds(client, requests_mock, bounds):
    with pytest.raises(ValueError):
        client.create_export(**bounds)
    assert not requests_mock.called


def test_list_exports(client, export, requests_mock):
    url = 'https://api.listenbrainz.org/1/export/list'
    requests_mock.get(url, json=[export])
    assert client.list_exports() == [export]
    assert requests_mock.last_request.headers['Authorization'] == 'Token test-token'
    requests_mock.get(url, json=[])
    assert client.list_exports() == []


@pytest.mark.parametrize('status', ['waiting', 'in_progress', 'completed', 'failed'])
def test_get_export(client, export, requests_mock, status):
    export['status'] = status
    export['start_time'] = 0
    export['end_time'] = 1769903999
    client.api_base_url = 'https://example.com/api/'
    requests_mock.get('https://example.com/api/1/export/123', json=export)
    assert client.get_export(123) == export
    assert requests_mock.last_request.headers['Authorization'] == 'Token test-token'


def test_delete_export(client, requests_mock):
    requests_mock.post('https://api.listenbrainz.org/1/export/123/delete', json={'success': True})
    assert client.delete_export(123) == {'success': True}
    assert requests_mock.last_request.headers['Authorization'] == 'Token test-token'
    assert requests_mock.last_request.body is None


def test_download_export(client, requests_mock, tmp_path):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w') as output:
        output.writestr('user.json', '{"id": 1, "name": "example"}')
        output.writestr('listens/2026/01.jsonl', b'\n' * (128 * 1024))
    requests_mock.get(
        'https://api.listenbrainz.org/1/export/123/download',
        content=archive.getvalue(),
        headers={
            'Content-Type': 'application/zip',
            'X-RateLimit-Remaining': '9',
            'X-RateLimit-Reset-In': '15',
        },
    )
    destination = tmp_path / 'history.zip'
    assert client.download_export(123, destination) == destination
    assert destination.read_bytes() == archive.getvalue()
    assert requests_mock.last_request.stream is True
    assert requests_mock.last_request.headers['Authorization'] == 'Token test-token'
    assert client.remaining_requests == 9
    assert client.ratelimit_reset_in == 15


def test_download_streams_and_closes_on_interruption(client, tmp_path):
    response = mock.MagicMock()
    response.__enter__.return_value = response
    response.status_code = 200
    response.headers = {}

    def chunks(chunk_size):
        assert chunk_size == 64 * 1024
        yield b'first chunk'
        yield b''
        raise requests.ConnectionError('interrupted')

    response.iter_content.side_effect = chunks
    destination = tmp_path / 'history.zip'
    with mock.patch('requests.Session.get', return_value=response) as get:
        with pytest.raises(requests.ConnectionError):
            client.download_export(123, str(destination))
    assert get.call_args.kwargs['stream'] is True
    response.json.assert_not_called()
    response.__exit__.assert_called_once()
    assert destination.read_bytes() == b'first chunk'


@pytest.mark.parametrize('method,verb,endpoint,args', [
    ('create_export', 'POST', '/1/export/', ()),
    ('list_exports', 'GET', '/1/export/list', ()),
    ('get_export', 'GET', '/1/export/123', (123,)),
    ('download_export', 'GET', '/1/export/123/download', (123,)),
    ('delete_export', 'POST', '/1/export/123/delete', (123,)),
])
@pytest.mark.parametrize('status', [400, 401, 404, 429, 503])
def test_export_errors(client, requests_mock, tmp_path, method, verb, endpoint, args, status):
    requests_mock.register_uri(
        verb, 'https://api.listenbrainz.org' + endpoint,
        status_code=status, json={'error': 'Request rejected'},
    )
    destination = tmp_path / 'history.zip'
    destination.write_bytes(b'existing archive')
    if method == 'download_export':
        args += (destination,)
    with pytest.raises(errors.ListenBrainzAPIException) as caught:
        getattr(client, method)(*args)
    assert caught.value.status_code == status
    assert caught.value.message == 'Request rejected'
    assert destination.read_bytes() == b'existing archive'


def test_download_non_json_error(client, requests_mock, tmp_path):
    requests_mock.get(
        'https://api.listenbrainz.org/1/export/123/download',
        status_code=404, text='Archive not found',
    )
    destination = tmp_path / 'history.zip'
    with pytest.raises(errors.ListenBrainzAPIException) as caught:
        client.download_export(123, destination)
    assert caught.value.status_code == 404
    assert caught.value.message is None
    assert not destination.exists()


def test_create_export_does_not_retry(client):
    def send(session, request, **kwargs):
        assert session.get_adapter(request.url).max_retries.total == 0
        raise requests.Timeout('response timed out')

    with mock.patch('requests.Session.send', autospec=True, side_effect=send) as send_request:
        with pytest.raises(requests.Timeout):
            client.create_export()
    assert send_request.call_count == 1
