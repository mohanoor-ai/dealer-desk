# System architecture

Reconciled 25 October 2026. This document describes the implemented system; deferred services are listed explicitly.

## Request and persistence path

React/TypeScript uses the central frontend/src/api.ts client for same-origin requests. FastAPI/Pydantic validates the contract; SQLAlchemy reads/writes business records; Alembic versions the schema. SQLite is the local default and PostgreSQL on Neon is the hosted database.

The public catalogue has a separate read-only response shape. It includes at most 100 non-archived internally marked reference listings, excluding known operational test makes. Only credited illustrative photo metadata/bytes can be exposed through catalogue routes. Staff notes, customer/enquiry/task records, users, revisions and audit events are excluded. Staff APIs require authenticated sessions.

Business relationships are Vehicle → Enquiry → Follow-up. Foreign keys preserve those links. Images and thumbnails are stored in database binary columns with caption/source/licence metadata. The API, rather than a serverless local filesystem, serves image bytes. Current bounded storage is portable across SQLite/PostgreSQL; R2 is not implemented.

## Staff security and concurrency

Operators provision individual users through an interactive CLI. Passwords use salted scrypt hashes. The database stores hashes of random eight-hour session tokens; the browser receives an HttpOnly/SameSite cookie with Secure enabled for hosted HTTPS. Logout revokes the session. Viewer reads; sales mutates stock/enquiries/tasks/photos; manager also accesses audit history. There is no public self-registration.

Backend permissions and same-origin mutation checks enforce access. Client button visibility is not an authorization boundary. A material edit atomically matches ID/revision, applies the new values and writes its audit event. A stale revision returns 409. Operational logs exclude customer messages and credentials.

## Interface state and task context

Saved staff snapshots load from paginated APIs and poll every three seconds without overlapping requests. HTTP errors leave a visible recovery path; lost authentication clears the staff view. Count/record links and scheduling preserve enquiry context through hash-route query parameters. Completing a task does not implicitly close its enquiry. Needs attention excludes closed enquiries and exposes unscheduled open work.

The catalogue and staff pages share styling but use different data boundaries. Internal reference markers are hidden in vehicle labels/editor input and preserved when staff saves an existing reference model.

Temporary customer/staff demos intercept business operations inside per-tab JavaScript memory, with no network fallback. They reset on refresh/end and reject operations after 30-minute expiry. No guest account, session cookie or browser storage is created. Background suspension can delay physical memory clearing until the tab resumes. Collections/text are bounded and photo uploads are unavailable in the simulation.

## Hosted environments and release

Vercel serves the built frontend and FastAPI. Production and development use different Neon branch endpoints; inherited database names do not imply a shared branch. The connection string remains server-side. Migrations run explicitly outside request/build startup.

Production browsing is public under Vercel Standard Protection; staff APIs still require app login. Development and preview deployments remain protected. Main triggers CI and development delivery, with the build waiting for successful trusted CI at the exact source SHA. Manual promotion advances production-release without force. Compatible cloud rollback/forward restoration was exercised separately from the isolated SQLite restore lab. Code rollback does not undo database contents or migrations.

## Local operations and extension boundaries

Opt-in OpenTelemetry SDK instrumentation exports bounded route/method/status/duration metadata and traces/logs/metric exemplars through OTLP HTTP/protobuf. A loopback-only custom receiver stores redacted batches in SQLite and provides a read-only correlation UI. Export is disabled unless configured; no hosted monitoring service is claimed.

Three failed authenticated stock reads trigger a deterministic responder against a fixed marked rehearsal database. Only a known table-rename fault can be repaired; unknown states escalate. It cannot execute arbitrary commands or access Neon. A separate read-only MCP stdio tool returns aggregate rehearsal counts. A specialist definition exists, but no independent invocation is claimed.

The course's Prometheus/Loki/Tempo/Grafana stack is not deployed. The project demonstrates collection/storage/correlation through its custom local implementation. See [operations](operations.md), [permissions](permissions.md), [release/recovery](release-recovery.md), [page map](site-map.md) and [verification](verification.md).
