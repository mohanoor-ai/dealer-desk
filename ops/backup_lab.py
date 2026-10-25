"""SQLite backup and independent restore check for the synthetic rehearsal only."""
import json
import sqlite3
from datetime import datetime, timezone
from ops.responder import ROOT, REHEARSAL_DB, authorize


def main():
    authorize(REHEARSAL_DB, 'restore_stock_table')
    destination = ROOT/'data'/('rehearsal-restored-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.sqlite3')
    with sqlite3.connect(REHEARSAL_DB.as_uri()+'?mode=ro', uri=True) as original:
        before = original.execute('SELECT count(*) FROM vehicles_v2').fetchone()[0]
        with sqlite3.connect(destination) as restored:
            original.backup(restored)
    with sqlite3.connect(destination.as_uri()+'?mode=ro', uri=True) as restored:
        after = restored.execute('SELECT count(*) FROM vehicles_v2').fetchone()[0]
        integrity = restored.execute('PRAGMA integrity_check').fetchone()[0]
    report = {'environment': 'synthetic-local-rehearsal', 'source_untouched': True,
              'restored_vehicle_count': after, 'counts_match': before == after,
              'integrity_check': integrity, 'independent_restore': True}
    if before != after or integrity != 'ok':
        raise RuntimeError('Independent restore verification failed.')
    (ROOT/'docs/evidence/backup-restore.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
