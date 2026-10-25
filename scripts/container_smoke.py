"""Synthetic API journey for disposable CI containers only. Never use on hosted data."""
import argparse
import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.request import Request, urlopen
from backend.auth import create_user, issue_session
from backend.database import build_engine, session_factory

STATE = Path('/tmp/dealer-ci-journey.json')


class Client:
    def __init__(self, token):
        self.token = token

    def send(self, method, path, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {'X-Requested-With': 'DealerDesk', 'Cookie': 'dealer_session='+self.token,
                   'Content-Type': 'application/json'}
        with urlopen(Request('http://127.0.0.1:8090'+path, data=data, headers=headers, method=method), timeout=5) as response:
            return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['create', 'verify'])
    args = parser.parse_args()
    if os.environ.get('DEALER_CI_REHEARSAL') != '1' or os.environ.get('VERCEL'):
        raise SystemExit('Only explicitly marked disposable CI containers are permitted.')
    if args.stage == 'create':
        engine = build_engine()
        with session_factory(engine)() as db:
            user = create_user(db, 'ci-'+secrets.token_hex(6), secrets.token_urlsafe(24), 'manager')
            token = issue_session(db, user)
        engine.dispose()
        client = Client(token)
        vehicle = client.send('POST', '/api/vehicles',
                              {'make': 'Synthetic', 'model': 'Container persistence', 'year': 2026, 'price_pence': 10000})
        enquiry = client.send('POST', '/api/enquiries',
                              {'vehicle_id': vehicle['id'], 'customer': 'Fictional CI buyer', 'message': 'Test only'})
        task = client.send('POST', '/api/tasks',
                           {'enquiry_id': enquiry['id'],
                            'due_date': datetime.now(ZoneInfo('Europe/London')).date().isoformat(), 'note': 'Synthetic check'})
        client.send('PATCH', f"/api/tasks/{task['id']}", {'revision': 1, 'completed': True})
        state = {'token': token, 'vehicle': vehicle['id'], 'task': task['id']}
        print(json.dumps({'stage': 'create', 'vehicle': state['vehicle'], 'task_completed': True}))
        # Printed state deliberately excludes the private cookie.
        print('JOURNEY_STATE='+json.dumps({'vehicle': state['vehicle'], 'task': state['task']}))
    else:
        # CI privately copies this cookie file across container replacement.
        state = json.loads(STATE.read_text())
        client = Client(state['token'])
        client.send('GET', f"/api/vehicles/{state['vehicle']}")
        tasks = client.send('GET', '/api/tasks')
        assert any(row['id'] == state['task'] and row['completed'] for row in tasks['items'])
        print(json.dumps({'stage': 'verify', 'records_preserved': True, 'task_completed': True}))
    STATE.write_text(json.dumps(state))
    STATE.chmod(0o600)


if __name__ == '__main__':
    main()
