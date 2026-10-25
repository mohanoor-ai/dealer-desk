# Project overview

Author: [Mohammed Sheikh-Noor](https://github.com/mohanoor-ai).

Dealer Desk connects vehicle availability, customer enquiries and follow-up work for one dealership. Staff can identify an enquiry without a next action, open the record directly and schedule the correct follow-up. Persistent records and revision checks support shared staff use.

## Current scope

Visitors browse a read-only reference catalogue and vehicle photos. Staff uses individual accounts with viewer/sales/manager roles to manage stock, enquiries and tasks. The overview distinguishes open enquiries from pending follow-ups; completing a task does not close the enquiry.

React/TypeScript/Vite connects to FastAPI/Pydantic, SQLAlchemy and Alembic. SQLite supports local development; hosted records/images use Neon PostgreSQL. Vercel hosts the frontend/API. Main CI gates development delivery; production promotion is explicit and uses a separate Neon branch. Compatible release rollback/forward restoration has been tested.

The local operations lab collects/correlates OpenTelemetry signals in a custom SQLite-backed UI, demonstrates a user-impact alert and a deterministic bounded repair, and tests an independent SQLite restore. It does not deploy Grafana/LGTM or invoke an LLM responder. Read-only MCP and reusable procedure/policy artifacts are demonstrated; no independent specialist invocation is claimed.

## Review route

- [Public website](https://dealer-desk-prod.vercel.app/): reference browsing without Vercel login; staff management requires an individual app account.
- [Development](https://dealer-desk-dev.vercel.app/): Vercel-protected.
- [Product specification](../product-spec.md), [setup](../README.md#run-locally) and [tests](testing.md).
- [Issue #5 execution example](issue-traceability.md), [assessment evidence](assessment-evidence.md) and [actual verification](verification.md).
- [Page map](site-map.md), [architecture](architecture.md) and [editable diagrams](diagrams.md).

Demonstration listings use reference prices/photos and are not offers for sale. Browser demos keep temporary per-tab records and do not write to the saved staff database. No real customer data or credentials belong in public documentation.

## Deferred scope and remaining assessment steps

Live website enquiry delivery, conversation/reply history, assignment, bulk upload, R2 and messaging integrations remain proposed. Production monitoring and independent specialist execution are not demonstrated. Local Docker Desktop remains unavailable; hosted CI verifies clean Compose and recovery. Submission requires student sign-in and the exact final commit; three assigned peer reviews follow. The documentation maps evidence and limitations rather than promising a grade.
