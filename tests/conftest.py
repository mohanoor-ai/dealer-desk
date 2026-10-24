from pathlib import Path
import os
from uuid import uuid4
import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.schema import CreateSchema, DropSchema
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from backend.app import create_app
from backend.auth import create_user
from backend.database import build_engine


@pytest.fixture
def test_database(tmp_path):
    target = os.environ.get('TEST_DATABASE_URL')
    if not target:
        yield 'sqlite:///' + (tmp_path / 'journey.sqlite3').as_posix()
        return
    parsed = make_url(target)
    if (parsed.get_backend_name() != 'postgresql' or parsed.host not in ('localhost', '127.0.0.1')
            or parsed.database != 'dealer_test'):
        raise ValueError('TEST_DATABASE_URL must point to local PostgreSQL dealer_test.')
    engine = build_engine(target)
    schema = 'test_' + uuid4().hex
    with engine.begin() as connection:
        connection.execute(CreateSchema(schema))
    try:
        yield parsed.update_query_dict({'options': '-csearch_path=' + schema}).render_as_string(hide_password=False)
    finally:
        # Only the randomly generated schema created above is disposable.
        with engine.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        engine.dispose()

@pytest.fixture
def app(test_database, monkeypatch):
    url = test_database
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
