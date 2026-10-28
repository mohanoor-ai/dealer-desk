"""Exercise the real smoke helper over loopback HTTP; Docker remains a separate layer."""
import json
import socket
import threading
import time
from contextlib import contextmanager
import pytest
import uvicorn
from sqlalchemy import update
from backend.app import create_app
from backend.models import MarketingPreference
from scripts import container_smoke as smoke


@contextmanager
def server(app,port):
    service=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=port,log_level='error',access_log=False))
    thread=threading.Thread(target=service.run,daemon=True);thread.start()
    deadline=time.monotonic()+10
    try:
        while not service.started:
            if time.monotonic()>deadline:raise RuntimeError('Loopback server did not start')
            time.sleep(.02)
        yield
    finally:
        service.should_exit=True;thread.join(timeout=10)
        assert not thread.is_alive()


def test_smoke_replacement_and_fingerprint_guard(app,tmp_path,monkeypatch,capsys):
    monkeypatch.setenv('DEALER_CI_REHEARSAL','1')
    monkeypatch.setenv('CUSTOMER_REGISTRATION_UNVERIFIED','true')
    monkeypatch.delenv('APP_ENV',raising=False);monkeypatch.delenv('VERCEL',raising=False)
    with socket.socket() as available:
        available.bind(('127.0.0.1',0));port=available.getsockname()[1]
    monkeypatch.setattr(smoke,'BASE_URL',f'http://127.0.0.1:{port}')
    monkeypatch.setattr(smoke,'STATE',tmp_path/'private-state.json')
    with server(app,port):
        monkeypatch.setattr('sys.argv',['container_smoke','create']);smoke.main()
    state=json.loads(smoke.STATE.read_text())
    restarted=create_app(app.state.engine.url.render_as_string(hide_password=False))
    try:
        with server(restarted,port):
            for stage in ['verify','verify-legacy','verify']:
                monkeypatch.setattr('sys.argv',['container_smoke',stage]);smoke.main()
            with restarted.state.sessions() as db:
                db.execute(update(MarketingPreference).values(opted_in=False));db.commit()
            with pytest.raises(AssertionError):smoke.main()
    finally:restarted.state.engine.dispose()
    output=capsys.readouterr().out
    private=[state['token'],state['customer_token'],'@example.com','Synthetic customer response','Synthetic staff response']
    if any(value in output for value in private):
        raise AssertionError('Smoke output contains private test data; details suppressed.')
    assert 'new_data_preserved' in output


def test_smoke_rejects_hosted_database_before_any_request(monkeypatch):
    from sqlalchemy.engine import make_url
    class HostedEngine:
        url=make_url('postgresql+psycopg://private@branch.neon.tech/dealer?sslmode=require')
        def dispose(self):pass
    monkeypatch.setenv('DEALER_CI_REHEARSAL','1')
    monkeypatch.delenv('VERCEL',raising=False);monkeypatch.delenv('APP_ENV',raising=False)
    monkeypatch.setattr(smoke,'build_engine',HostedEngine)
    monkeypatch.setattr('sys.argv',['container_smoke','verify'])
    with pytest.raises(SystemExit,match='disposable'):smoke.main()
