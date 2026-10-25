import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
from backend.config import database_url, secure_cookies
from backend.database import build_engine


@pytest.fixture(autouse=True)
def local_environment(monkeypatch):
    for name in ('VERCEL', 'APP_ENV', 'DATABASE_URL', 'COOKIE_SECURE'):
        monkeypatch.delenv(name, raising=False)


def test_local_database_and_cookie_defaults():
    assert database_url() == 'sqlite:///data/dealer-v2.sqlite3'
    assert not secure_cookies()


def test_health_identifies_revision_without_echoing_invalid_environment(client, monkeypatch):
    monkeypatch.setenv('VERCEL_GIT_COMMIT_SHA', 'a'*40)
    response = client.get('/health')
    assert response.status_code == 200 and response.json()['revision'] == 'a'*40
    monkeypatch.setenv('VERCEL_GIT_COMMIT_SHA', 'private-invalid-value')
    response = client.get('/health')
    assert response.json()['revision'] == 'unknown'
    assert 'private-invalid-value' not in response.text


@pytest.mark.parametrize('value', [None, 'sqlite:///:memory:', 'postgresql://user:private@host/db'])
def test_hosted_runtime_rejects_missing_persistent_secure_storage(monkeypatch, value):
    monkeypatch.setenv('VERCEL', '1')
    if value:
        monkeypatch.setenv('DATABASE_URL', value)
    with pytest.raises(RuntimeError) as error:
        database_url()
    assert 'private' not in str(error.value)


def test_hosted_postgres_uses_psycopg_tls_and_no_local_pool(monkeypatch):
    monkeypatch.setenv('VERCEL', '1')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://user:private@localhost/db?sslmode=require')
    monkeypatch.setenv('COOKIE_SECURE', 'false')
    engine = build_engine()
    assert engine.url.drivername == 'postgresql+psycopg'
    assert engine.url.query['sslmode'] == 'require'
    assert isinstance(engine.pool, NullPool)
    assert secure_cookies()
    engine.dispose()


def test_invalid_url_error_does_not_echo_credentials():
    with pytest.raises(RuntimeError, match='DATABASE_URL is invalid'):
        database_url('private invalid credential')


def test_hosted_login_sets_secure_cookie(client, monkeypatch):
    # The fixture has already created its isolated local test database.
    monkeypatch.setenv('VERCEL', '1')
    response = client.post('/api/auth/login', json={
        'username': 'manager', 'password': 'fictional-test-password'})
    assert response.status_code == 200
    assert '; Secure' in response.headers['set-cookie']


def test_frontend_documents_are_not_cached(tmp_path, monkeypatch):
    from backend import app as app_module
    frontend = tmp_path / 'frontend' / 'dist'
    frontend.mkdir(parents=True)
    (frontend / 'index.html').write_text('<html><body>Demo</body></html>')
    monkeypatch.setattr(app_module, 'ROOT', tmp_path)
    application = app_module.create_app('sqlite:///:memory:')
    with TestClient(application) as browser:
        for path in ('/', '/index.html'):
            response = browser.get(path)
            assert response.status_code == 200
            assert response.headers['cache-control'] == 'no-store'
        recovery = browser.get('/assets/index-old123.js')
        assert recovery.status_code == 200
        assert recovery.headers['content-type'].startswith('application/javascript')
        assert recovery.headers['cache-control'] == 'no-store'
        assert 'url.searchParams.get("release")===release' in recovery.text
        assert 'window.location.replace(url.href)' in recovery.text
        assert browser.get('/assets/unrelated.js').status_code == 404
        assets = frontend / 'assets'
        assets.mkdir()
        (assets / 'index-present123.js').write_text('console.log("present")')
        assert browser.get('/assets/index-present123.js').text == 'console.log("present")'
        (assets / 'index-present123.css').write_text('body{color:black}')
        stylesheet = browser.get('/assets/index-present123.css')
        assert stylesheet.status_code == 200
        assert stylesheet.headers['content-type'].startswith('text/css')
        assert browser.get('/assets/index-missing123.css').status_code == 404
    config = json.loads((Path(__file__).resolve().parents[1] / 'vercel.json').read_text())
    for path in ('/', '/index.html'):
        rule = next(item for item in config['headers'] if item['source'] == path)
        assert {'key': 'Cache-Control', 'value': 'no-store'} in rule['headers']
