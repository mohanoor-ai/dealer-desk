"""Pinned prior application against the current disposable SQLite schema, not Docker."""
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tarfile
import time
from urllib.request import urlopen
from contextlib import contextmanager
from scripts import container_smoke as smoke

PRIOR='0efadbc32abcd7e372f59f4f03f9a080f1068d1f'
ROOT=Path(__file__).resolve().parents[1]


@contextmanager
def application(source,port,environment,tmp_path,label):
    with (tmp_path/(label+'.log')).open('wb') as logs:
        process=subprocess.Popen([sys.executable,'-m','uvicorn','backend.app:app',
            '--host','127.0.0.1','--port',str(port),'--no-access-log'],cwd=source,
            env=environment,stdout=logs,stderr=logs)
        try:
            deadline=time.monotonic()+20
            while True:
                if process.poll() is not None:raise RuntimeError('Isolated application exited: '+label)
                try:
                    with urlopen(f'http://127.0.0.1:{port}/health',timeout=.5) as response:
                        assert response.status==200
                    break
                except OSError:
                    if time.monotonic()>deadline:raise RuntimeError('Isolated application startup timed out')
                    time.sleep(.05)
            yield
        finally:
            process.terminate()
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)


def test_pinned_previous_application_preserves_new_records(app,tmp_path,monkeypatch,capsys):
    # This layer deliberately tests SQLite; CI separately exercises PostgreSQL containers.
    if app.state.engine.dialect.name!='sqlite':
        import pytest
        pytest.skip('SQLite process rehearsal; container CI covers PostgreSQL')
    archive=subprocess.run(['git','archive',PRIOR],cwd=ROOT,check=True,capture_output=True).stdout
    previous=tmp_path/'previous';previous.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as packed:
        packed.extractall(previous,filter='data')
    with socket.socket() as available:
        available.bind(('127.0.0.1',0));port=available.getsockname()[1]
    monkeypatch.setenv('DEALER_CI_REHEARSAL','1');monkeypatch.setenv('CUSTOMER_REGISTRATION_UNVERIFIED','true')
    monkeypatch.delenv('VERCEL',raising=False);monkeypatch.delenv('APP_ENV',raising=False)
    monkeypatch.setattr(smoke,'STATE',tmp_path/'private-state.json')
    monkeypatch.setattr(smoke,'BASE_URL',f'http://127.0.0.1:{port}')
    environment=dict(os.environ)
    for label,source,stages in [('current',ROOT,['create','verify']),
                                 ('previous',previous,['verify-legacy']),
                                 ('restored',ROOT,['verify'])]:
        with application(source,port,environment,tmp_path,label):
            for stage in stages:
                monkeypatch.setattr('sys.argv',['container_smoke',stage]);smoke.main()
    output=capsys.readouterr().out
    assert 'new_data_preserved' in output
    print(json.dumps({'prior':PRIOR,'schema':'20261027_public_writes',
        'database':'disposable SQLite','legacy_read_write':True,
        'new_records_preserved':True,'current_customer_workflows_restored':True}))
