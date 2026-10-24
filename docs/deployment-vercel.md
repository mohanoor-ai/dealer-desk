# Vercel development deployment runbook

Status: protected Vercel development deployment and Neon migrations verified on 24 October 2026. Hosted address: https://dealer-desk-dev.vercel.app/. Project-specific All Deployments authentication is enabled. Public release remains blocked by the items below; see verification.md for actual results and commits.

## Build and runtime
Root directory is the application repository, not frontend/. Select the FastAPI framework. app.py exports the existing ASGI app. vercel.json builds the React/Vite frontend using python -m scripts.build_vercel. Only generated public/ assets are served by the CDN. Existing hash routes need no wildcard rewrite that could capture /api. Python is pinned to 3.12; Node 24 is the frontend target. The platform build/import and hosted journey have passed for the recorded deployment.

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
- Migrations and hosted upload processing passed. Complete the least-privilege runtime/migration-role split and broader cold-start/proxy/host review; keep credentials private.
- Current frontend polling must pause when hidden and reduce idle usage.
- PostgreSQL photo persistence and hosted redeployment checks passed. Complete current-image Compose replacement and backup/restore checks.
- R2 implementation is planned; current photos still live in database binary fields. No R2 credentials, bucket or migration exists yet.
- Hosted CI and automatic Vercel Git deployment work. CI-gated delivery/manual promotion, telemetry, impact alert, responder and rollback evidence remain pending.

## Account step after local preparation
The owner connects the reviewed public repository or authorizes a scoped Vercel CLI connection, selects the existing personal Vercel account and development Neon project, and enters database secrets directly into hosting settings. No paid subscription is needed for this personal project within quotas. Confirm public/private inventory before source publication. Keep this first deployment protected; public release is a separate gate after the blockers above are resolved.

Official configuration reference checked 24 October 2026: https://vercel.com/docs/frameworks/backend/fastapi


## Staff account setup
Run the operator command against the intended database: uv run python -m scripts.create_user manager --role manager. It prompts privately for the password and stores a salted hash in Neon. Creating the account changes database records, so it does not require a code push or redeployment. The owner reported creating the manager password on 24 October 2026; successful hosted manager sign-in still needs confirmation. The convenience launcher and local database connection file remain outside this repository. Never commit account rows, password hashes or secrets.
