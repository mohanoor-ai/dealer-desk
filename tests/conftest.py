from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from backend.app import create_app
from backend.auth import create_user

@pytest.fixture
def app(tmp_path, monkeypatch):
    url = 'sqlite:///' + (tmp_path / 'journey.sqlite3').as_posix()
    monkeypatch.setenv('DATABASE_URL', url)
    config = Config(str(Path(__file__).parents[1] / 'alembic.ini'))
    command.upgrade(config, 'head')
    app = create_app(url)
    with app.state.sessions() as db:
        for username, role in [('manager', 'manager'), ('sales', 'sales'), ('viewer', 'viewer')]:
            create_user(db, username, 'fictional-test-password', role)
    yield app
    app.state.engine.dispose()

@pytest.fixture
def client(app):
    with TestClient(app, headers={'X-Requested-With': 'DealerDesk'}) as client:
        yield client

def sign_in(client, username='manager'):
    response = client.post('/api/auth/login', json={'username': username, 'password': 'fictional-test-password'})
    assert response.status_code == 200, response.text
    return response

@pytest.fixture
def signed_client(client):
    sign_in(client)
    return client
