"""Built UI falls back only for HTML navigation; API and private files stay separate."""
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image
import pytest

from app.main import create_app


@pytest.fixture
def built_client(tmp_path):
    dist = tmp_path / 'dist'
    (dist / 'assets').mkdir(parents=True)
    (dist / 'index.html').write_text('<!doctype html><title>Built scanner</title>')
    (dist / 'assets/app.js').write_text('console.log("built")')
    (dist / 'secret.txt').write_text('private-dist-file')
    (tmp_path / 'secret.txt').write_text('outside-dist-file')
    with TestClient(create_app(tmp_path / 'data/scanner.sqlite3', frontend_dir=dist)) as client:
        yield client


def test_built_home_navigation_reload_assets_and_api_share_origin(built_client):
    client = built_client
    for path in ['/', '/?session=example', '/document/example', '/index.html']:
        response = client.get(path, headers={'Accept': 'text/html'})
        assert response.status_code == 200 and 'Built scanner' in response.text
        assert response.headers['content-type'].startswith('text/html')
        assert response.headers['cache-control'] == 'no-cache'
    asset = client.get('/assets/app.js')
    assert asset.status_code == 200 and 'console.log' in asset.text
    assert 'javascript' in asset.headers['content-type']
    assert asset.headers['x-content-type-options'] == 'nosniff'
    assert client.get('/api/v1/health').json() == {'status': 'ok'}
    assert client.post('/api/v1/health').status_code == 405
    assert client.get('/api/v1/sessions/00000000-0000-4000-8000-000000000001/pages').status_code == 405


@pytest.mark.parametrize('path', [
    '/api', '/api/v1/missing', '/api/v1/artifacts/not-a-uuid',
    '/data', '/data/scanner.sqlite3', '/backend/app/main.py', '/experiments',
    '/.git/config', '/secret.txt', '/assets/missing.js',
    '/assets/%2e%2e/%2e%2e/secret.txt', '/assets/%2e%2e/secret.txt',
    '/assets/..%5c..%5csecret.txt', '/document/file.png',
])
def test_missing_api_asset_private_path_and_traversal_never_return_spa(built_client, path):
    response = built_client.get(path, headers={'Accept': 'text/html'})
    assert response.status_code == 404
    assert response.headers['content-type'].startswith('application/json')
    assert 'private-dist-file' not in response.text and 'outside-dist-file' not in response.text


def test_fallback_requires_html_and_preserves_api_artifact_after_reload(built_client):
    client = built_client
    assert client.get('/document/example', headers={'Accept': 'application/json'}).status_code == 404
    assert client.post('/document/example').status_code == 404
    sid = client.post('/api/v1/sessions', json={'title': 'Same origin'}).json()['id']
    stream = BytesIO()
    Image.new('RGB', (80, 100), 'white').save(stream, format='PNG')
    imported = client.post(f'/api/v1/sessions/{sid}/pages', files={'file': ('page.png', stream.getvalue(), 'image/png')})
    assert imported.status_code == 201
    page = imported.json()
    detail = client.get(f'/api/v1/sessions/{sid}').json()
    assert detail['pages'][0]['id'] == page['id']
    source = client.get('/api/v1/artifacts/' + page['normalized_artifact_id'])
    assert source.status_code == 200 and source.headers['content-type'] == 'image/png'
    assert client.get(f'/?session={sid}', headers={'Accept': 'text/html'}).status_code == 200
    assert client.get('/api/v1/artifacts/' + page['normalized_artifact_id']).content == source.content
    assert client.get(f'/api/v1/sessions/{sid}').json() == detail
    assert len(client.get('/openapi.json').json()['paths']) == 12


def test_missing_build_and_explicit_api_only_mode_do_not_break_health(tmp_path):
    for frontend in [tmp_path / 'missing-dist', None]:
        with TestClient(create_app(tmp_path / 'data/scanner.sqlite3', frontend_dir=frontend)) as client:
            assert client.get('/api/v1/health').json() == {'status': 'ok'}
            assert client.get('/', headers={'Accept': 'text/html'}).status_code == 404
