"""Alert on three consecutive failed authenticated stock reads; bounded local recovery."""
import time
from datetime import datetime, timezone
import requests
from ops.responder import REHEARSAL_DB, respond


def probe(session, base):
    if base != 'http://127.0.0.1:8791':
        raise PermissionError('Monitor may only target the fixed loopback rehearsal service.')
    try:
        response = session.get(base+'/api/vehicles', timeout=3)
        return {'status': response.status_code, 'trace_id': response.headers.get('X-Trace-ID')}
    except requests.RequestException:
        return {'status': 0, 'trace_id': None}


def monitor(session, base='http://127.0.0.1:8791', interval=1):
    failures = []
    for _ in range(3):
        result = probe(session, base)
        if result['status'] == 200:
            return {'alert': False, 'probes': failures+[result]}
        failures.append(result)
        time.sleep(interval)
    alert = {'name': 'StockReadUnavailable', 'at': datetime.now(timezone.utc).isoformat(),
             'condition': '3 consecutive authenticated stock reads failed', 'probes': failures}
    # The actual failed journey triggers this deterministic response agent.
    action = respond(REHEARSAL_DB)
    recovered = probe(session, base)
    return {'alert': alert, 'response': action, 'recovery': recovered,
            'recovered': recovered['status'] == 200}
