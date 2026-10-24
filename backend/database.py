from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from backend.config import database_url, hosted

def build_engine(url=None):
    url = database_url(url)
    if url.startswith('sqlite:///') and ':memory:' not in url:
        Path(url.removeprefix('sqlite:///')).parent.mkdir(parents=True, exist_ok=True)
    options = {'pool_pre_ping': True}
    if hosted():
        # Neon provides external pooling; do not multiply idle pools per function.
        options.update(poolclass=NullPool, connect_args={'connect_timeout': 10})
    engine = create_engine(url, **options)
    if engine.dialect.name == 'sqlite':
        @event.listens_for(engine, 'connect')
        def enable_foreign_keys(connection, record):
            connection.execute('PRAGMA foreign_keys=ON')
    return engine

def session_factory(engine):
    return sessionmaker(engine, expire_on_commit=False)
