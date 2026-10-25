"""Opt-in OTLP signals. Export only bounded route metadata, never request content."""
import os
import re
from contextlib import contextmanager
from urllib.parse import urlsplit

from opentelemetry import trace
from opentelemetry._logs import SeverityNumber
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter


def collector_endpoint(value):
    parsed = urlsplit(value)
    if (parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost', 'telemetry')
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ('', '/')):
        raise ValueError('Telemetry collector must be a local HTTP endpoint without credentials.')
    return value.rstrip('/')


class Telemetry:
    def __init__(self):
        endpoint = os.environ.get('DEALER_OTLP_ENDPOINT')
        self.providers = []
        self.tracer = trace.NoOpTracer()
        self.counter = self.duration = self.log = None
        if not endpoint:
            return
        endpoint = collector_endpoint(endpoint)
        revision = os.environ.get('APP_REVISION', 'local')
        if not re.fullmatch(r'[a-f0-9]{40}|local', revision):
            raise ValueError('APP_REVISION must be a full Git SHA or local.')
        resource = Resource.create({'service.name': 'dealer-desk', 'service.version': revision,
                                    'deployment.environment.name': 'local-rehearsal'})
        spans = TracerProvider(resource=resource)
        spans.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint+'/v1/traces', timeout=2)))
        reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=endpoint+'/v1/metrics', timeout=2),
                                              export_interval_millis=2000)
        metrics = MeterProvider(resource=resource, metric_readers=[reader])
        logs = LoggerProvider(resource=resource)
        logs.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint+'/v1/logs', timeout=2)))
        self.providers = [spans, metrics, logs]
        self.tracer = spans.get_tracer('dealer.http')
        meter = metrics.get_meter('dealer.http')
        self.counter = meter.create_counter('dealer.http.requests', unit='{request}')
        self.duration = meter.create_histogram('dealer.http.duration', unit='ms')
        self.log = logs.get_logger('dealer.http')

    @contextmanager
    def request(self):
        # Disable automatic exception recording: exception text may contain data.
        with self.tracer.start_as_current_span('HTTP request', record_exception=False,
                                               set_status_on_exception=False) as span:
            yield span

    def finish(self, span, route, method, status, duration_ms):
        method = method if method in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS') else 'OTHER'
        fields = {'http.route': route, 'http.request.method': method,
                  'http.response.status_code': status}
        span.update_name(method + ' ' + route)
        span.set_attributes(fields)
        if status >= 500:
            span.set_status(trace.Status(trace.StatusCode.ERROR))
        if self.counter:
            self.counter.add(1, fields)
            self.duration.record(duration_ms, fields)
            self.log.emit(body='http.request.completed', severity_number=SeverityNumber.INFO,
                          attributes={**fields, 'duration_ms': round(duration_ms, 2)})

    def flush(self):
        for provider in self.providers:
            provider.force_flush(timeout_millis=5000)

    def shutdown(self):
        for provider in self.providers:
            provider.shutdown()
