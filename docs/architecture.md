# System architecture

Reconciled 25 October 2026. This document describes the implemented system; deferred services are listed explicitly.

## Request and persistence path

React/TypeScript uses the central frontend/src/api.ts client for same-origin requests. FastAPI/Pydantic validates the contract; SQLAlchemy reads/writes business records; Alembic versions the schema. SQLite is the local default and PostgreSQL on Neon is the hosted database.

The public catalogue has a separate read-only response shape. It includes at most 100 non-archived internally marked reference listings, excluding known operational test makes. Only credited illustrative photo metadata/bytes can be exposed through catalogue routes. Staff notes, customer/enquiry/task records, users, revisions and audit events are excluded. Staff APIs require authenticated sessions.

Business relationships are Vehicle → Enquiry → Follow-up. Foreign keys preserve those links. Images and thumbnails are stored in database binary columns with caption/source/licence metadata. The API, rather than a serverless local filesystem, serves image bytes. Current bounded storage is portable across SQLite/PostgreSQL; R2 is not implemented.

## Staff security and concurrency

Operators provision individual users through an interactive CLI. Passwords use salted scrypt hashes. The database stores hashes of random eight-hour session tokens; the browser receives an HttpOnly/SameSite cookie with Secure enabled for hosted HTTPS. Logout revokes the session. Viewer reads; sales mutates stock/enquiries/tasks/photos; manager also accesses audit history. Staff accounts have no public self-registration; separate local customer registration is described below.

Backend permissions and same-origin mutation checks enforce access. Client button visibility is not an authorization boundary. A material edit atomically matches ID/revision, applies the new values and writes its audit event. A stale revision returns 409. Operational logs exclude customer messages and credentials.

## Interface state and task context

Saved staff snapshots load from paginated APIs and poll every three seconds without overlapping requests. HTTP errors leave a visible recovery path; lost authentication clears the staff view. Count/record links and scheduling preserve enquiry context through hash-route query parameters. Completing a task does not implicitly close its enquiry. Needs attention excludes closed enquiries and exposes unscheduled open work.

The catalogue and staff pages share styling but use different data boundaries. Internal reference markers are hidden in vehicle labels/editor input and preserved when staff saves an existing reference model.

When the saved demo is explicitly started, the central API client fetches the public catalogue if no dataset exists and seeds same-origin browser storage. Saved enquiries, tasks, vehicle edits, photo metadata and customer-visible messages are shared between its customer/staff views and open tabs. Active roles remain per-tab; refresh resumes an unexpired 30-minute session. End/sign-out retains the dataset, while explicit Reset clears it and restores the starting public snapshot. No business request falls through to the real API while demo mode is active. Images use the existing public photo endpoint; uploads remain unavailable. This is a device-local test simulation, with no customer authentication, database transactions or cross-device sharing. Normal customer accounts and saved business records use SQL and server authorization instead. See customer-continuity.md.


## Hosted environments and release

Vercel serves the built frontend and FastAPI. Production and development use different Neon branch endpoints; inherited database names do not imply a shared branch. The connection string remains server-side. Migrations run explicitly outside request/build startup.

Production browsing is public under Vercel Standard Protection; staff APIs still require app login. Development and preview deployments remain protected. Main triggers CI and development delivery, with the build waiting for successful trusted CI at the exact source SHA. Manual promotion advances production-release without force. Compatible cloud rollback/forward restoration was exercised separately from the isolated SQLite restore lab. Code rollback does not undo database contents or migrations.

## Local operations and extension boundaries

Opt-in OpenTelemetry SDK instrumentation exports bounded route/method/status/duration metadata and traces/logs/metric exemplars through OTLP HTTP/protobuf. A loopback-only custom receiver stores redacted batches in SQLite and provides a read-only correlation UI. Export is disabled unless configured; no hosted monitoring service is claimed.

Three failed authenticated stock reads trigger a deterministic responder against a fixed marked rehearsal database. Only a known table-rename fault can be repaired; unknown states escalate. It cannot execute arbitrary commands or access Neon. A separate read-only MCP stdio tool returns aggregate rehearsal counts. A specialist definition exists, but no independent invocation is claimed.

The course's Prometheus/Loki/Tempo/Grafana stack is not deployed. The project demonstrates collection/storage/correlation through its custom local implementation. See [operations](operations.md), [permissions](permissions.md), [release/recovery](release-recovery.md), [page map](site-map.md) and [verification](verification.md).

## Public project articles

Fourteen authored articles live as Markdown under docs/articles. Vite bundles those sources and the referenced public screenshots into the frontend; the Docker build copies those public source directories into its frontend build stage. No GitHub request is needed to load article text/images. The public hash routes #/learning and #/learning/<slug> resolve against the current app origin. Rendering uses React text/link elements, not raw HTML. Repository implementation references remain ordinary outbound source links. Public reading requires no staff account; private learning notes and transcripts are not included.

## Local saved enquiry workflow — awaiting release

The 26 October source extends the normal customer and staff app, beyond the optional demo. A vehicle-specific dialog posts a bounded public request to /api/catalogue/enquiries; it returns only a reference. Only published catalogue vehicles or an explicit general enquiry are accepted. Source is fixed to Website, submission keys prevent duplicate retry records, same-origin middleware applies, and a local bounded process limiter rejects excess attempts. The hosted environment rejects this route pending release approval and shared abuse controls.

Normal staff sessions read sources/request types/contact details, use request-based editable next actions, and save staff-confirmed reply/contact/outcome activity. Create/reply plus optional follow-up commits atomically; enquiry revision checks reject stale actions. An enquiry row write lock serializes closure with task insertion/reopening. Closing requires an outcome and no pending tasks. Email uses encoded mailto drafts, not a delivery provider.

Migration 20261026_enquiry_workflow preserves existing IDs/references, permits general enquiries without an invented vehicle, and adds bounded contact/activity fields and a unique private submission key. Source defaults to Other for historical rows. Code rollback across this schema change has not been verified and must not reuse the earlier compatible rollback claim. Only the separate local preview database has been backed up and migrated; Neon and production remain unchanged. The shared UI also operates on temporary demo records through the existing central API interception. See local-enquiry-demo.md for testing.

## Local customer continuity — 27 October 2026

Normal local customer accounts, hashed sessions/action tokens and owned enquiry conversations now use separate SQL tables and a separate cookie. Verification/recovery links are single-use and expiring; local preview links explicitly simulate email delivery and do not prove real inbox ownership. Hosted registration/recovery remains disabled. A verified local account claims only unowned matching-email enquiries; each customer list/thread request enforces ownership. Customer responses omit internal tasks/activity. Staff/customer in-account messages update response attention and persist independently of external email confirmations.

The optional demo now shares test snapshots in same-origin local storage, with per-tab active roles and a 30-minute session. Data remains after refresh or ending a session until explicit reset/browser clearing. It does not use the customer SQL account tables or business network writes. This supersedes the earlier memory-only demo behaviour; it is not shared cloud storage or real authentication. Comparison is in-memory; viewed IDs persist only after the optional choice. Global policy pages describe these actual boundaries. See customer-continuity.md and review-sources.md.

## Registration without email verification

The owner-approved optional CUSTOMER_REGISTRATION_UNVERIFIED=true setting enables customer signup and sign-in without claiming email ownership. New accounts retain verified=false. Only enquiries submitted while authenticated are attached to these accounts; matching email never grants earlier guest conversations. Hosted verification previews and password reset remain disabled. Registration and login use shared database request budgets. Configure this setting only on the intended hosted project after schema migration and exact-commit CI. This does not send email or enable email-based account recovery.
