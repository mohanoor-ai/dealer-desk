# Local telemetry, alert and recovery

This development lab uses the real application and an isolated synthetic SQLite database. It does not inject faults into Vercel or Neon. The response agent is deterministic, not an LLM.

## Run

After `uv sync --frozen`, open two terminals in the repository:

```sh
uv run python -m ops.collector
```

```sh
uv run python -m ops.rehearse
uv run python -m ops.backup_lab
```

Open http://127.0.0.1:8790/ for the read-only operations UI. It displays stored OTLP exports and a table joining spans, request logs and sampled metric exemplars by trace ID. Expand a batch to inspect the actual signal. The collector binds only to loopback and retains at most 1,000 batches. This is not a production telemetry platform.

The rehearsal refuses to overwrite an existing data/rehearsal.sqlite3. Preserve or move that synthetic database before a new run. The database, authorization marker, process output and independent restore copies remain private under ignored data/. No seeded password or raw session appears in the public reports.

## Actual incident

The script migrates an isolated database, creates a random-credential synthetic identity and saves a vehicle through the real HTTP API. It temporarily renames only the stock table. Three consecutive authenticated GET /api/vehicles failures trigger StockReadUnavailable. The response agent checks the fixed database/marker/environment, inspects table presence read-only, and restores the table only if the known fault matches. It then repeats the same stock read and checks the saved vehicle remains. Unknown conditions escalate rather than run arbitrary commands.

The actual retained report is [incident-rehearsal.json](evidence/incident-rehearsal.json): three 503 responses, a fixed-action repair, recovery to 200 and record preservation. [backup-restore.json](evidence/backup-restore.json) records a separate SQLite backup restored into an independent file, matching count and integrity_check=ok. This is not a Neon recovery exercise or evidence of an LLM making the decision.

![Actual local operations UI showing request correlation](evidence/operations-correlation.png)

Capture: 25 October 2026; loopback rehearsal; fictional records only. Initial signals came from the uncommitted operations implementation based on 3298b5f, not the unchanged application at that commit. The emitted service.version initially used that base revision; do not treat it as an immutable build attestation. CI reruns the rehearsal against the actual checked-out source and uploads its own report.

## Signal boundary

backend/telemetry.py uses OpenTelemetry SDK and OTLP HTTP/protobuf exporters. Set DEALER_OTLP_ENDPOINT to a loopback collector only when running the lab. Without it, telemetry is disabled. Exports include route templates, method, status, duration, trace/span identifiers and service/version/environment metadata. Request bodies, query strings, headers, session cookies, customer fields and exception text are excluded. No trace ID is used as a metric label; correlation uses sampled exemplars.

The stored dashboard proves collection/storage/viewing locally. It is not Grafana, and no Grafana Cloud deployment is claimed. The original LGTM stack remains a possible production-oriented alternative, not a prerequisite for this lab.

## Verification

tests/test_operations.py sends real OTLP signals to a real loopback collector and checks collection, correlation, invalid payloads, egress restrictions and data-preserving guardrails. tests/test_mcp.py exercises actual stdio MCP initialization, tool discovery, a read-only call and denial of an unknown write tool. CI also runs the complete HTTP fault/repair rehearsal and independent restore.
