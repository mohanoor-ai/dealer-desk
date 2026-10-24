import pytest
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
