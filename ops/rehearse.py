"""Reproduce a real local stock failure, automatic alert/repair and data-preserving recovery."""
import json
import os
import secrets
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
import requests
from alembic import command
from alembic.config import Config
from backend.auth import create_user, issue_session
from backend.database import build_engine, session_factory
from ops.responder import ROOT, REHEARSAL_DB, MARKER
from ops.watch import monitor


def wait_ready(base):
    for _ in range(45):
        try:
            if requests.get(base+'/health', timeout=1).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    raise RuntimeError('Local rehearsal service did not become ready.')


def main():
    os.chdir(ROOT)
    if REHEARSAL_DB.exists():
        raise SystemExit('Existing rehearsal preserved. Move it aside before creating another rehearsal.')
    if os.environ.get('VERCEL') or os.environ.get('APP_ENV') in ('production', 'staging'):
        raise SystemExit('Rehearsal cannot run in a hosted environment.')
    REHEARSAL_DB.parent.mkdir(exist_ok=True)
    url = 'sqlite:///'+REHEARSAL_DB.as_posix()
    os.environ['DATABASE_URL'] = url
    command.upgrade(Config('alembic.ini'), 'head')
    engine = build_engine(url)
    with session_factory(engine)() as db:
        user = create_user(db, 'rehearsal', secrets.token_urlsafe(32), 'manager')
        token = issue_session(db, user)
    engine.dispose()
    session = requests.Session()
    session.cookies.set('dealer_session', token)
    session.headers['X-Requested-With'] = 'DealerDesk'
    env = {**os.environ, 'DATABASE_URL': url, 'DEALER_OTLP_ENDPOINT': 'http://127.0.0.1:8790',
           'APP_REVISION': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    output = ROOT/'data/rehearsal-process.txt'
    with output.open('w', encoding='utf-8') as log:
        child = subprocess.Popen([sys.executable, 'start.py', '--port', '8791'], env=env,
                                 stdout=log, stderr=log)
        try:
            wait_ready('http://127.0.0.1:8791')
            initial = session.post('http://127.0.0.1:8791/api/vehicles', timeout=5,
                                   json={'make': 'Synthetic', 'model': 'Recovery proof', 'year': 2026,
                                         'price_pence': 1234500})
            initial.raise_for_status()
            record_id = initial.json()['id']
            MARKER.write_text(json.dumps({'incident': 'stock_table_unavailable'}))
            with sqlite3.connect(REHEARSAL_DB) as db:
                db.execute('ALTER TABLE vehicles_v2 RENAME TO vehicles_v2_rehearsal_offline')
            report = monitor(session)
            final = session.get('http://127.0.0.1:8791/api/vehicles', timeout=5)
            report['record_preserved'] = any(row['id'] == record_id for row in final.json()['items'])
            report['responder_type'] = 'deterministic policy agent, not an LLM'
            report['environment'] = 'isolated loopback SQLite rehearsal; no hosted fault'
            report['source_commit'] = env['APP_REVISION']
            report['source_has_uncommitted_changes'] = bool(subprocess.check_output(['git', 'diff', '--name-only']))
            time.sleep(7)  # Allow batched real OTLP exports before orderly shutdown.
            (ROOT/'docs/evidence/incident-rehearsal.json').write_text(json.dumps(report, indent=2))
            print(json.dumps(report, indent=2))
            if not report['recovered'] or not report['record_preserved']:
                raise RuntimeError('Recovery verification failed.')
        finally:
            child.terminate()
            child.wait(timeout=15)
            session.close()


if __name__ == '__main__':
    main()
