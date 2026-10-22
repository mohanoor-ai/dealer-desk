from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from backend import auth
from backend.models import LoginSession
from conftest import sign_in

def test_passwords_are_salted_and_verified():
    first = auth.hash_password('a-long-test-password')
    second = auth.hash_password('a-long-test-password')
    assert first != second
    assert auth.verify_password('a-long-test-password', first)
    assert not auth.verify_password('wrong-password', first)

def test_authentication_and_revoked_session(client):
    assert client.get('/api/vehicles').status_code == 401
    assert client.post('/api/auth/login', json={'username':'manager','password':'incorrect'}).status_code == 401
    login = sign_in(client)
    cookie = login.headers['set-cookie'].lower()
    assert 'httponly' in cookie and 'samesite=strict' in cookie
    token = client.cookies.get(auth.COOKIE)
    assert client.get('/api/auth/me').json()['username'] == 'manager'
    assert client.post('/api/auth/logout').status_code == 204
    client.cookies.set(auth.COOKIE, token)
    assert client.get('/api/auth/me').status_code == 401

def test_expired_session_rejected(client, app):
    sign_in(client)
    with app.state.sessions() as db:
        session = db.scalar(select(LoginSession))
        session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    assert client.get('/api/auth/me').status_code == 401

def test_viewer_cannot_write_or_read_audit(client):
    sign_in(client, 'viewer')
    assert client.get('/api/vehicles').status_code == 200
    assert client.post('/api/vehicles', json={'make':'Demo','model':'City','year':2020,'price_pence':10}).status_code == 403
    assert client.get('/api/audit').status_code == 403

def test_cross_site_mutations_rejected(client):
    response = client.post('/api/auth/login', headers={'Sec-Fetch-Site':'cross-site'},
                           json={'username':'manager','password':'fictional-test-password'})
    assert response.status_code == 403

def test_login_rate_limit(client):
    for _ in range(10):
        assert client.post('/api/auth/login', json={'username':'manager','password':'wrong'}).status_code == 401
    assert client.post('/api/auth/login', json={'username':'manager','password':'wrong'}).status_code == 429
