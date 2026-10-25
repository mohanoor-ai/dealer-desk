# Dealer Desk — project overview

Author: [Mohammed Sheikh-Noor](https://github.com/mohanoor-ai).

Dealer Desk helps staff at one dealership keep vehicle availability, enquiries and the next follow-up action together. It replaces disconnected stock and task lists with a shared persistent workspace.

## Current implementation

- Staff accounts with viewer, sales and manager permissions enforced by the API.
- Vehicle search, filters, detail pages, photo galleries and bounded photo uploads.
- Enquiries linked to stock, with follow-up scheduling and completion.
- Database persistence, revision checks for conflicting edits and an audit trail.
- React/TypeScript frontend, FastAPI backend, SQLAlchemy and Alembic; SQLite locally or PostgreSQL, including Neon for hosting.

## Links and review access

- [Hosted development app](https://dealer-desk-dev.vercel.app/): Vercel authorization followed by a provisioned staff login.
- [Repository](https://github.com/mohanoor-ai/dealer-desk).
- [Setup instructions](../README.md#start-with-docker).
- [Verification and limitations](verification.md).
- [Current and planned diagrams](diagrams.md).

Temporary browser demos use fictional data in per-tab memory. They do not demonstrate shared database persistence. Use fictional records when reviewing the persistent staff application too. Credentials must be supplied privately, never committed here.

## Remaining work

Independent staff-session conflict/refresh, exact-commit CI gating, clean CI Compose startup, image rollback/forward recovery, local correlated operational signals, a real deterministic alert/repair exercise and the read-only MCP extension are verified. Separate protected production promotion is being configured. No LLM diagnosis or independently invoked specialist is claimed. R2 storage and a public customer showroom are planned. This description does not claim final assessment readiness.
