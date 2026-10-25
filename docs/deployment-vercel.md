# Vercel and Neon deployment runbook

Current environments: [public production](https://dealer-desk-prod.vercel.app/) and [protected development](https://dealer-desk-dev.vercel.app/). Public browsing and staff authentication are separate boundaries. See [environment configuration](environments.md) and [actual verification](verification.md).

## Build and runtime

Use the repository root and FastAPI framework. app.py exports the ASGI application; vercel.json invokes `python -m scripts.build_vercel`. That command waits for trusted successful main CI at the exact source SHA before installing/building the frontend, then copies generated frontend/dist files to public/. Vercel serves those generated assets; hash routes need no wildcard rewrite that could capture /api.

Python 3.12 and Node.js 24 are the selected runtime/build targets. A local build can use `uv run python -m scripts.build_vercel`; the CI guard activates in Vercel. The guard/build never connects to or migrates a database.

.vercelignore excludes runtime data, environment files, tests/docs and bundled reference originals. Photo bytes/credits required by the interface are served through the API/database. Server connection strings are not frontend environment variables.

## Secrets and environment separation

Store the intended Neon pooled connection in server-side DATABASE_URL with sslmode=require or stronger. The runtime uses the installed psycopg dialect and NullPool. Hosted startup rejects missing database configuration, SQLite and PostgreSQL without TLS. Hosted cookies are Secure automatically.

Development and production use distinct Neon branch endpoints. The production connection is a Production-only secret in its separate Vercel project, not attached to unrelated previews. No connection strings or passwords belong in source, chat, screenshots or command output. Account provisioning and migrations use an authorized private operator connection; this document does not claim separately provisioned least-privilege migration/runtime roles.

Development/previews retain Vercel protection. At the owner's request, the production alias permits public browsing under Standard Protection. Staff APIs still require an individual app session. The optional customer/staff browser demos are memory-only simulations behind one footer entry, not guest database accounts.

## Migrations, account setup and release

1. Confirm the intended environment and recovery plan before changing an existing database. Never use the development connection by accident for production.
2. Inject DATABASE_URL privately into the trusted operator environment. Run `uv run alembic upgrade head` explicitly, serialized per target. Builds, imports and requests do not run migrations.
3. Create a staff account with `uv run python -m scripts.create_user manager --role manager`. The password prompt is interactive; a salted hash is stored. Provisioning changes database records and does not require a code redeploy. Owner-reported manager sign-in and temporary hosted staff checks are recorded separately in verification.md.
4. Let main CI complete and inspect the development build/health source revision and relevant saved workflow.
5. Invoke `uv run python -m scripts.promote <full-sha>` for the reviewed revision. It verifies trusted CI and advances production-release without force; Vercel builds the same source revision.
6. Check production /health revision and relevant workflow. Anonymous catalogue reads should succeed; anonymous private staff reads should return 401. Retain actual results.
7. Roll back only to a compatible known-good release, then verify recovery. Code rollback does not undo database contents or migrations. Test database restore separately in an isolated target.

[Release/recovery](release-recovery.md) records tested cloud and container recovery, with limits. [Verification](verification.md) links the exact observed revisions and CI runs.

## Remaining operational limits

The login limiter is process-local. Distributed throttling, public enquiry-write controls, background/idle polling optimization, managed telemetry and a hosted Neon restore drill remain outside the demonstrated deployment. Current polling is every three seconds. Photos remain database-backed; R2 is not configured. These limits do not justify inventing a connected integration or calling a real dealership deployment production-ready.

Configuration reference used during setup: [Vercel FastAPI documentation](https://vercel.com/docs/frameworks/backend/fastapi). No service/plan changes are made by this documentation update.
