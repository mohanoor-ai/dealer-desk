import json
import sqlite3
import threading
from http.server import ThreadingHTTPServer
import pytest
import requests
from backend.telemetry import Telemetry, collector_endpoint
from ops.collector import handler, store, read, summary
from ops import responder


def test_real_otlp_collection_and_privacy(tmp_path, monkeypatch):
    path = tmp_path/'signals.sqlite3'
    store(path, 'logs', {})
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler(path))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv('DEALER_OTLP_ENDPOINT', f'http://127.0.0.1:{server.server_port}')
    telemetry = Telemetry()
    try:
        with telemetry.request() as span:
            trace_id = format(span.get_span_context().trace_id, '032x')
            telemetry.finish(span, '/api/vehicles', 'GET', 503, 12.3)
        telemetry.flush()
        rows = read(path)
        signals = {row['signal'] for row in rows}
        assert signals == {'traces', 'metrics', 'logs'}
        encoded = json.dumps(rows)
        assert trace_id in encoded
        assert 'dealer.http.requests' in encoded
        logs = json.dumps([row for row in rows if row['signal'] == 'logs'])
        traces = json.dumps([row for row in rows if row['signal'] == 'traces'])
        assert trace_id in logs and trace_id in traces
        assert any(row['trace_id'] == trace_id and row['log'] and row['metric_exemplar'] for row in summary(rows))
        assert 'customer' not in encoded and 'password' not in encoded
        assert requests.post(f'http://127.0.0.1:{server.server_port}/v1/traces',
                             data=b'invalid', headers={'Content-Type': 'application/x-protobuf'}).status_code == 400
    finally:
        telemetry.shutdown()
        server.shutdown()
        server.server_close()


@pytest.mark.parametrize('endpoint', ['https://example.com', 'http://user:secret@localhost',
                                      'http://127.0.0.1/path', 'http://localhost?secret=x'])
def test_collector_rejects_egress_and_secrets(endpoint):
    with pytest.raises(ValueError):
        collector_endpoint(endpoint)


def test_responder_guard_and_data_preserving_repair(tmp_path, monkeypatch):
    database = tmp_path/'isolated.sqlite3'
    marker = tmp_path/'authorized.json'
    monkeypatch.setattr(responder, 'REHEARSAL_DB', database)
    monkeypatch.setattr(responder, 'MARKER', marker)
    monkeypatch.delenv('VERCEL', raising=False)
    monkeypatch.delenv('APP_ENV', raising=False)
    with pytest.raises(PermissionError):
        responder.respond(database)
    marker.write_text(json.dumps({'incident': 'stock_table_unavailable'}))
    with sqlite3.connect(database) as db:
        db.execute('CREATE TABLE vehicles_v2_rehearsal_offline(id INTEGER)')
        db.execute('INSERT INTO vehicles_v2_rehearsal_offline VALUES(7)')
    with pytest.raises(PermissionError):
        responder.authorize(database, 'arbitrary_sql')
    with pytest.raises(PermissionError):
        responder.respond(tmp_path/'production.sqlite3')
    assert responder.respond(database)['changed'] is True
    with sqlite3.connect(database) as db:
        assert db.execute('SELECT id FROM vehicles_v2').fetchone() == (7,)
    assert responder.respond(database)['action'] == 'escalate'
    monkeypatch.setenv('VERCEL', '1')
    with pytest.raises(PermissionError):
        responder.respond(database)
