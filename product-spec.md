# Dealer Desk product specification

Status: current implemented scope, reconciled 25 October 2026. Deferred capabilities are listed separately. Detailed observations remain in [verification](docs/verification.md).

## Problem and users

A single dealership needs a shared record of vehicle availability, customer enquiries and the next staff action. Separate stock and task lists make it difficult to see which enquiries are unanswered or unscheduled, and concurrent edits can overwrite newer information.

| User | Expected access |
|---|---|
| Visitor | Browse reference listings and vehicle details without a staff account |
| Viewer | Read staff records after signing in; no mutations |
| Sales staff | Manage stock, photos, enquiries and follow-up tasks |
| Manager | Sales capabilities plus manager-only audit access |
| Operator | Provision staff accounts and run authorized migrations/releases through documented commands |

The hosted deployment contains demonstration records and historical reference prices; its website enquiry delivery remains disabled. The 26 October local source supports saved website enquiries and the staff workflow described below, pending release review. No shared staff password is published.

## Expected workflows

### Vehicle browsing

The landing page shows selected reference listings and compact browsing links. Visitors search/filter the catalogue, switch thumbnail/list layout and open a vehicle detail page. Details show price context, availability and credited illustrative photos. Contact details are not invented when none have been supplied. At widths up to 760px, top and bottom three-bar controls open a vertical customer or staff menu. The modal supports keyboard dismissal, focus return and current-page indication.

The read-only catalogue includes at most 100 non-archived listings marked internally for demonstration, excluding operational test makes. Responses contain listing fields and credited illustrative photo metadata, not staff notes, customer records, accounts or audit events. Photo delivery repeats that publication check.

### Staff stock management

Staff sign in to their own account, add a vehicle, inspect its detail/gallery and edit its information or availability. Prices are integer pence. Status is available, reserved or sold. Images are decoded, bounded, metadata-stripped and re-encoded before storage. Uploaded JPEG/PNG/WebP files are limited to 2 MiB each and twelve photos per vehicle. A cover photo can be selected.

An edit includes the revision originally opened. The server applies the change only if the revision still matches; otherwise it returns 409 and the staff member refreshes/reviews the newer record. A material change and its audit event commit together.

### Enquiry and next action

Staff records source, request type, customer name, contact details and message against an existing active vehicle or as a general enquiry. Customers open a vehicle-specific popup from Send an enquiry, with no vehicle choice unless they explicitly select a different/general query. Request categories suggest editable staff next actions. Website submissions set source Website and return a minimal saved reference; the hosted write route remains disabled. Enquiry status is new, contacted or closed. The overview counts non-closed enquiries and identifies each enquiry's customer, vehicle, request and pending next action.

An open enquiry without an incomplete follow-up says No next action scheduled. Clicking the count opens open enquiries; an enquiry number opens that exact record. Schedule follow-up carries the enquiry ID to the form. Staff chooses a due date and task note. The UK dealership date distinguishes overdue, due-today and upcoming tasks.

Staff can record a manually confirmed email reply or contact outcome, with actual actor/time/activity. Opening a mailto draft does not change status or prove sending. Optional follow-up fields create the enquiry/reply and task atomically. Closing requires an outcome and no pending tasks. Staff can complete/reopen a task. Task completion does not close the enquiry or send a reply. If the enquiry remains open with no other pending task, it appears as unscheduled again. Closed enquiries do not appear in overview attention.

### Saved and simulated workflows

Authenticated staff operations use the API and persistent database. Shared views poll every three seconds. The explicitly requested saved customer/staff demo intercepts business operations and shares test snapshots in browser local storage. Active role/session state is per tab, expires after 30 minutes and resumes after refresh; ending a session retains the dataset until reset. It does not create real customer accounts, cloud enquiries or staff sessions. These are distinct verification boundaries.

## Data and backend behaviour

Vehicle: ID, make/model, year, price_pence, approved facts, status, archived flag, revision and timestamps. Photos retain captions, credit, source/licence metadata, dimensions and processed image/thumbnail bytes.

Enquiry: ID, optional vehicle foreign key, source, request type, customer display name, email/phone, bounded message, status, bounded activity, closure outcome, private submission key, revision and timestamps. Follow-up: ID, enquiry foreign key, due date, note, completed flag, revision and timestamps.

Foreign keys preserve relationships. Pydantic rejects unknown fields and invalid types/ranges. SQLAlchemy uses bound parameters. Individual passwords use salted scrypt hashes; only session-token hashes are stored. Session cookies are HttpOnly/SameSite and Secure on hosted HTTPS. Roles are enforced on the server; same-origin mutation guards apply to writes. The [OpenAPI contract](openapi.yaml) describes inputs, outputs and errors.

## Core technical acceptance criteria

| ID | Acceptance criterion | Verification route |
|---|---|---|
| V1 | Valid vehicle creation returns 201/ID; invalid values and unknown fields are rejected; values persist | tests/test_journey.py |
| V2 | Active-stock search/filter/pagination work; archive access is explicit | tests/test_journey.py; staff stock UI |
| V3 | A stale revision returns 409 without overwriting newer data | tests/test_journey.py; manual two-session evidence |
| V4 | Valid status edits are saved with an actor/revision audit event | tests/test_journey.py |
| P1 | Photo type/size/dimensions, metadata removal, quota, persistence and cover selection are checked | tests/test_photos.py |
| E1 | Enquiries reference an existing unarchived vehicle or explicitly represent a general enquiry; invalid IDs and archived conflicts are rejected | tests/test_journey.py |
| E2 | Follow-up validation, complete/reopen and persisted counts agree | tests/test_journey.py |
| E3 | Count/number links, unscheduled state, correct preselection, task completion and viewer controls work | frontend/src/workflow.test.tsx; README collage |
| C1 | Public catalogue omits private/archived/test data and disallowed photos; staff APIs remain authenticated | tests/test_catalogue.py; anonymous hosted checks |
| U1 | Forms and API client provide loading, error and empty states; user text is rendered safely | frontend tests; manual browser checks; full accessibility audit not completed |
| U2 | Independent sessions observe changes within five seconds and stale edits fail | three-second polling; retained manual independent-session check |
| D1 | Versioned migrations and the same app support SQLite/PostgreSQL; no migrations occur at request/build startup | Alembic; database/hosting tests; PostgreSQL CI |
| T1 | One fail-fast command runs backend/frontend tests, build and limited source audit | scripts/verify.py; hosted CI output |
| R1 | Compose runs app/PostgreSQL and retains records after app replacement | startup scripts; clean Compose HTTP journey in CI |
| R2 | Exact-revision CI gates delivery; production promotion is explicit; compatible rollback/forward restoration is exercised | scripts/release_gate.py; scripts/promote.py; release/recovery evidence |
| O1 | A key journey emits redacted metrics/logs/traces, collected/stored and correlated in a UI | local OTLP receiver; tests/test_operations.py; operations.md |
| O2 | A real user-impact alert invokes a bounded responder; the same failed request recovers or escalates | isolated local fault/repair rehearsal; no LLM invocation |
| A1 | Read-only MCP, reusable procedure, specialist definition and enforced policy have explicit permissions | extension pack; MCP/policy tests; independent specialist invocation not demonstrated |
| S1 | Actual source/dependency scan findings and their disposition are retained with scope/limits | security/review.md; security JSON reports; limited scanner |

New demos copy the current public catalogue before activating; they do not use a fixed three-car fixture. Bootstrap failure or an empty catalogue leaves the demo inactive with an error. Reset restores that starting snapshot and a new session fetches the catalogue again.

## Public project journal

Visitors can read fourteen authored project articles without staff login, available through direct public URLs. Article links are relative to the app origin and sources/images ship with the build. Markdown remains readable in the repository; private notes/transcripts are excluded. Each post identifies its author/date and course hashtag.

## Implementation and delivery

React/TypeScript/Vite → central API client → FastAPI/Pydantic → SQLAlchemy → SQLite locally or PostgreSQL on Neon. Alembic controls migrations. Database-backed photos avoid reliance on a serverless filesystem.

Vercel hosts the built frontend and API. Main builds wait for trusted exact-revision CI; an operator advances production-release after checks. Development and production use separate Neon branches. Production browsing is public; staff records require app login. Development/previews remain Vercel-protected.

Local OpenTelemetry exports feed a custom loopback SQLite collector/correlation UI. Prometheus, Loki, Tempo and Grafana are taught by the course but are not deployed here. The isolated responder performs one deterministic guarded repair, with no arbitrary command tool or hosted database access. See [architecture](docs/architecture.md), [operations](docs/operations.md) and [release controls](docs/release-recovery.md).

## Deferred and excluded scope

Local saved workflow awaiting release: website submission with local abuse bounds, staff-confirmed reply/contact history and optional atomic follow-up (see docs/local-enquiry-demo.md). Hosted delivery and shared abuse controls remain deferred; incoming reply synchronisation remains deferred; staff assignment; bulk upload; R2 migration; email/WhatsApp/SMS integrations; Grafana/LGTM deployment; independent specialist execution; an optional in-app LLM with separate provider/evaluation controls.

Excluded: payments, marketplace publishing, vehicle-history/valuation claims, real customer operations, multi-tenant SaaS, model training/RAG and autonomous production repair. Public learning articles describe actual work; private lesson notes/transcripts and secrets stay outside Git.

## Completion and assessment

Implemented work requires source, runnable checks and actual evidence; targets do not count as demonstrations. The [public tracker](https://github.com/mohanoor-ai/dealer-desk/issues), [task record](docs/tasks.md) and [worked traceability example](docs/issue-traceability.md) connect acceptance criteria to execution.

The [assessment evidence index](docs/assessment-evidence.md) maps the current project to the pinned course rubric. It is not a grade guarantee. Final course submission and three assigned peer reviews remain separate owner steps.

## Local customer continuity update — 27 October 2026

Pending release, the normal local app adds separate customer registration/login, local verification/recovery previews and owner-checked enquiry conversations. Guest enquiries link only after verification with matching email; local previews simulate inbox verification, and hosted signup is disabled until a real delivery service is configured. Customers continue an existing thread after signing in. Staff in-account messages are distinct from manual email confirmations and internal notes.

The receipt returns to the vehicle and offers viewed/browse links without Start another enquiry. A session reference prevents reopening the same car as a new form. Compare allows up to three vehicles using verified stored fields; stars appear only for dated publisher/model matches. Optional viewed history is off before consent. Privacy/Cookies/Terms are global. The demo is now a shared, persistent test dataset on the same browser until reset, with separate per-tab active roles; it remains separate from actual dealership data and customer accounts. See docs/customer-continuity.md.
