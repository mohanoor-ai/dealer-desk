"""Only aggregate counts from the fixed synthetic rehearsal database."""
import sqlite3
from ops.responder import REHEARSAL_DB


def stock_summary():
    if not REHEARSAL_DB.exists():
        return {'available': False, 'reason': 'Run the isolated rehearsal first.'}
    with sqlite3.connect(REHEARSAL_DB.as_uri()+'?mode=ro', uri=True) as db:
        rows = db.execute('SELECT status, count(*) FROM vehicles_v2 WHERE archived=0 GROUP BY status').fetchall()
    return {'available': True, 'environment': 'synthetic-local-rehearsal',
            'counts': {status: count for status, count in rows}}
