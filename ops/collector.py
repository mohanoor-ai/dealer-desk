"""Loopback OTLP/protobuf receiver with bounded SQLite storage and a read-only UI."""
import argparse
import base64
import html
import json
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import DecodeError
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest

TYPES = {'traces': ExportTraceServiceRequest, 'metrics': ExportMetricsServiceRequest,
         'logs': ExportLogsServiceRequest}
SAFE_ATTRIBUTES = {'service.name', 'service.version', 'deployment.environment.name',
                   'http.route', 'http.request.method', 'http.response.status_code', 'duration_ms'}


def redact(value):
    if isinstance(value, list):
        return [redact(item) for item in value[:500]]
    if not isinstance(value, dict):
        return value
    result = {}
    for key, item in value.items():
        if key == 'attributes':
            result[key] = [redact(attr) for attr in item if attr.get('key') in SAFE_ATTRIBUTES]
        elif key in ('traceId', 'spanId'):
            result[key] = base64.b64decode(item).hex()
        elif key == 'body':
            result[key] = {'stringValue': 'http.request.completed'}
        elif key in ('events', 'links', 'description'):
            continue
        else:
            result[key] = redact(item)
    return result


def store(path, signal, payload):
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS signals(id INTEGER PRIMARY KEY, at TEXT, signal TEXT, payload TEXT)')
        db.execute('INSERT INTO signals(at,signal,payload) VALUES(?,?,?)',
                   (datetime.now(timezone.utc).isoformat(), signal, json.dumps(payload)))
        db.execute('DELETE FROM signals WHERE id <= (SELECT coalesce(max(id),0)-1000 FROM signals)')


def read(path):
    with sqlite3.connect(path) as db:
        return [{'id': row[0], 'at': row[1], 'signal': row[2], 'payload': json.loads(row[3])}
                for row in db.execute('SELECT id,at,signal,payload FROM signals ORDER BY id DESC LIMIT 60')]


def summary(rows):
    spans, logs, exemplars = {}, set(), set()
    def visit(value):
        if isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, dict):
            for span in value.get('spans', []):
                fields = {item['key']: next(iter(item['value'].values())) for item in span.get('attributes', [])}
                spans[span.get('traceId')] = fields
            for record in value.get('logRecords', []):
                logs.add(record.get('traceId'))
            for exemplar in value.get('exemplars', []):
                exemplars.add(exemplar.get('traceId'))
            for child in value.values():
                visit(child)
    for row in rows:
        visit(row['payload'])
    return [{'trace_id': trace_id, **fields, 'log': trace_id in logs, 'metric_exemplar': trace_id in exemplars}
            for trace_id, fields in spans.items()]


def handler(database):
    class Receiver(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, status, data, content_type):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'")
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            signal = self.path.removeprefix('/v1/')
            try:
                length = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                self.respond(400, b'Invalid length', 'text/plain')
                return
            if (signal not in TYPES or self.path != '/v1/'+signal or length <= 0 or length > 4_000_000
                    or self.headers.get('Content-Type') != 'application/x-protobuf'
                    or self.headers.get('Origin')):
                self.respond(400, b'Invalid OTLP request', 'text/plain')
                return
            try:
                message = TYPES[signal]()
                message.ParseFromString(self.rfile.read(length))
                store(database, signal, redact(MessageToDict(message)))
            except (DecodeError, ValueError):
                self.respond(400, b'Invalid protobuf', 'text/plain')
                return
            self.respond(200, b'', 'application/x-protobuf')

        def do_GET(self):
            rows = read(database)
            if self.path == '/signals':
                self.respond(200, json.dumps(rows).encode(), 'application/json')
                return
            if self.path != '/':
                self.respond(404, b'Not found', 'text/plain')
                return
            table = '<section><h2>Request correlation</h2><table><tr><th>Journey</th><th>Status</th><th>Trace ID</th><th>Log</th><th>Metric exemplar</th></tr>'
            for record in summary(rows):
                cells = [str(record.get('http.request.method', ''))+' '+str(record.get('http.route', '')),
                         str(record.get('http.response.status_code', '')), record['trace_id'],
                         'collected' if record['log'] else 'not found',
                         'collected' if record['metric_exemplar'] else 'not sampled']
                table += '<tr>'+''.join('<td>'+html.escape(cell)+'</td>' for cell in cells)+'</tr>'
            table += '</table></section>'
            sections = ''.join('<details><summary>'+html.escape(row['signal'])+' · '+html.escape(row['at'])+
                               '</summary><pre>'+html.escape(json.dumps(row['payload'], indent=2))+'</pre></details>'
                               for row in rows)
            counts = {name: sum(row['signal'] == name for row in rows) for name in TYPES}
            page = ('<!doctype html><html lang="en"><meta charset="utf-8"><title>Dealer Desk operations</title>'
                    '<meta name="viewport" content="width=device-width,initial-scale=1"><style>'
                    'body{font:16px system-ui;margin:32px auto;max-width:1100px;padding:16px;background:#f3f6f5;color:#142f2b}'
                    'section,details{background:white;padding:20px;margin:20px 0;border-radius:12px}pre{overflow:auto;font-size:13px}'
                    'table{border-collapse:collapse;width:100%;font-size:13px}td,th{text-align:left;padding:12px 6px;border-bottom:1px solid #ddd;overflow-wrap:anywhere}'
                    '</style><h1>Dealer Desk · local operations</h1><p>Stored real OTLP exports. '
                    'Refresh to view new signals. Trace IDs connect request logs, spans and metric exemplars.</p><p>'
                    +html.escape(str(counts))+'</p>'+table+'<h2>Stored OTLP batches</h2>'+sections+'</html>')
            self.respond(200, page.encode(), 'text/html; charset=utf-8')
    return Receiver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', default='data/telemetry.sqlite3')
    parser.add_argument('--port', type=int, default=8790)
    args = parser.parse_args()
    path = Path(args.database)
    path.parent.mkdir(parents=True, exist_ok=True)
    store(path, 'logs', {'notice': 'Collector started; no application signal claimed.'})
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler(path))
    print(f'Local operations UI: http://127.0.0.1:{args.port}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
