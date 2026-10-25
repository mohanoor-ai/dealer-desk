"""Deterministic, bounded local responder. No model-generated commands or production access."""
import json
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REHEARSAL_DB = ROOT / 'data' / 'rehearsal.sqlite3'
MARKER = ROOT / 'data' / 'rehearsal-authorized.json'


def authorize(path, action):
    if (Path(path).resolve() != REHEARSAL_DB.resolve() or action != 'restore_stock_table'
            or REHEARSAL_DB.is_symlink() or REHEARSAL_DB.parent.is_symlink() or MARKER.is_symlink()
            or os.environ.get('VERCEL') or os.environ.get('APP_ENV') in ('production', 'staging')):
        raise PermissionError('Only the isolated local rehearsal and fixed restore action are permitted.')
    if not MARKER.exists() or json.loads(MARKER.read_text()).get('incident') != 'stock_table_unavailable':
        raise PermissionError('Explicit rehearsal authorization marker is required.')


def diagnose(path):
    authorize(path, 'restore_stock_table')
    with sqlite3.connect(Path(path).as_uri()+'?mode=ro', uri=True) as db:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    return {'vehicle_table_present': 'vehicles_v2' in tables,
            'rehearsal_table_present': 'vehicles_v2_rehearsal_offline' in tables}


def respond(path):
    authorize(path, 'restore_stock_table')
    evidence = diagnose(path)
    if evidence != {'vehicle_table_present': False, 'rehearsal_table_present': True}:
        return {'action': 'escalate', 'evidence': evidence, 'changed': False}
    # Fixed, reviewed recovery; input can never become SQL or a shell command.
    with sqlite3.connect(path) as db:
        db.execute('ALTER TABLE vehicles_v2_rehearsal_offline RENAME TO vehicles_v2')
    return {'action': 'restore_stock_table', 'evidence': evidence, 'changed': True,
            'after': diagnose(path)}
