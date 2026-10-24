# Vercel development deployment runbook

Status: configuration prepared locally; hosted compatibility and publication remain unverified. This is a private development deployment until release blockers are resolved.

## Build and runtime
Root directory is the application repository, not frontend/. Select the FastAPI framework. app.py exports the existing ASGI app. vercel.json builds the React/Vite frontend using python -m scripts.build_vercel. Only generated public/ assets are served by the CDN. Existing hash routes need no wildcard rewrite that could capture /api. Python is pinned to 3.12; Node 24 is the frontend target. A platform build/import is still required to validate the selected runtime combination.

Local check: uv run python -m scripts.build_vercel. Then start.py can serve frontend/dist locally. .vercelignore excludes runtime databases, private environment files, tests, docs and bundled reference originals. Credits needed by the rendered UI remain in database metadata. Generated frontend files contain no server secrets.

## Environment separation
Create a Vercel development/preview project first with Vercel Authentication protection left enabled. Never remove protection while the shared limiter and demo isolation remain incomplete. Use a development Neon database with fictional data and its own role. Release credentials must never be attached to arbitrary previews.

Set DATABASE_URL in Vercel's server-side environment settings using Neon's pooled PostgreSQL URL with sslmode=require (or stronger). The runtime converts postgresql:// to the installed psycopg dialect and uses NullPool so each function does not retain an idle connection pool. Hosted runtime refuses missing DATABASE_URL, SQLite and PostgreSQL URLs without TLS. Cookies are automatically Secure on Vercel/staging/production.

Keep migration credentials separate from runtime credentials. Create the first staff account through the trusted operator command against the intended database, with an interactive password prompt. Do not store a shared default password in the repository or run account creation on every function invocation. Customer and dealer demo buttons are future work.

## Migrations and promotion
1. Back up an existing target database; for a new target confirm it is empty.
2. In a trusted shell/CI job, inject the target database migration URL into DATABASE_URL using the secret store (do not paste secrets into chat, commands/history or logs).
3. Run uv run alembic upgrade head once, serialized per environment. The Vercel build and ASGI import do not run migrations.
4. Build/deploy a protected preview for the same commit using the runtime DB role; keep schema changes additive and backward compatible.
5. Verify /health, the login screen, secure login/logout, authorization, create/read/edit and photo uploads. Check state survives a subsequent deployment. Record actual URL, SHA, workflow run and screenshots after access is available.
6. Promote only a tested immutable deployment. Roll back code using the prior known-good deployment; never assume this reverses schema/data changes. Test restore separately in a fresh database.

## Release blockers
- Process-local login throttling must become shared and atomic before public access.
- Add global upload/demo quotas, isolated resettable demo data and public/staff response boundaries.
- Verify hosted DB privileges, migrations, secure cookies, upload processing, cold start and proxy/host behaviour.
- Current frontend polling must pause when hidden and reduce idle usage.
- Complete PostgreSQL photo persistence/container refresh and backup/restore tests.
- R2 implementation is planned; current photos still live in database binary fields. No R2 credentials, bucket or migration exists yet.
- Hosted CI/CD, telemetry, impact alert, responder and rollback evidence remain pending.

## Account step after local preparation
The owner connects the reviewed public repository or authorizes a scoped Vercel CLI connection, selects the existing personal Vercel account and development Neon project, and enters database secrets directly into hosting settings. No paid subscription is needed for this personal project within quotas. Confirm public/private inventory before source publication. Keep this first deployment protected; public release is a separate gate after the blockers above are resolved.

Official configuration reference checked 24 October 2026: https://vercel.com/docs/frameworks/backend/fastapi
