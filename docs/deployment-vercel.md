# Vercel and Neon deployment how-to

Current environments: [public production](https://dealer-desk-prod.vercel.app/) and [protected development](https://dealer-desk-dev.vercel.app/). Public browsing and staff authentication are separate boundaries. See [environment configuration](environments.md) and [actual verification](verification.md).

## Recreate the cloud deployment

These steps create a separate working application using your own [Vercel](https://vercel.com/) and [Neon](https://neon.com/) accounts. Opening the existing public website demonstrates availability; reproducing the setup requires the source, dependencies, configuration, schema and checks below. No credentials or hosted database contents are supplied with the repository.

### 1. Prepare your repository and workstation

Install Git, Python 3.12+, uv and Node.js 24. For local app/PostgreSQL startup, use the [Docker Compose instructions](../README.md#docker-compose); Docker is not needed to provision Vercel/Neon from the workstation. CI uses Docker on its own runner.

Create a public fork or repository copy, enable its GitHub Actions, then clone it. Replace YOUR_ACCOUNT with its owner:

```sh
git clone https://github.com/YOUR_ACCOUNT/dealer-desk.git
cd dealer-desk
uv sync --frozen
npm ci --prefix frontend
```

The build gate is intentionally tied to the original repository. For a fork, set `REPOSITORY` in [scripts/release_gate.py](../scripts/release_gate.py) to your actual `owner/repository`. Update the matching repository identity in [tests/test_release_gate.py](../tests/test_release_gate.py). Retain the rejection test for an unrelated fork. Do not disable the gate. Commit those changes on `main`, push and run/check:

```sh
uv run python -m scripts.verify
```

Wait for the trusted main push workflow to finish successfully and retain its full commit SHA. CI runs additional PostgreSQL, container and recovery stages. A private fork is not supported by this unauthenticated public-GitHub gate as written.

### 2. Create separate Neon database targets

Create your Neon project and separate development/production branches or projects. Starting from a fresh empty database avoids copying another environment's accounts or sessions. If you intentionally branch an existing database, it inherits that snapshot; review its data and revoke copied sessions before using it as an independent environment.

Use **Connect** in the Neon console and select the intended branch, database and role. Keep two connection forms for each target: pooled for the serverless app and direct for the serialized operator migration/provisioning step. Preserve the console's TLS parameters, including `sslmode=require` or stronger. See [Neon connection details](https://neon.com/docs/connect/connect-from-any-app) and [pooling](https://neon.com/docs/connect/connection-pooling).

The connection hostname identifies the branch endpoint; an inherited database name alone does not establish isolation. Store credentials privately. Do not paste them into Git, screenshots, articles or frontend variables.

### 3. Initialize each database and manager account

From the checkout, run the following once per intended target. The prompt hides the direct Neon connection string and passes it only to the child operator commands; the manager password is prompted separately by create_user. This uses the actual migration and provisioning scripts, without adding credentials to shell history:

```sh
uv run python -c "import getpass,os,subprocess,sys; os.environ['DATABASE_URL']=getpass.getpass('Direct Neon connection string: '); os.environ['APP_ENV']='production'; subprocess.run([sys.executable,'-m','alembic','upgrade','head'],check=True); subprocess.run([sys.executable,'-m','scripts.create_user','manager','--role','manager'],check=True)"
```

Confirm the selected target before running migrations. The manager command creates an account; it does not reset an existing account's password. Build/import/request handling does not initialize the hosted schema automatically. Verify the schema revision through the migration output before deploying.

A fresh database contains no vehicle listings, staff enquiries or uploaded photos. Sign in and create your own review vehicle, enquiry and follow-up to test persistence. The ten existing hosted reference cars and licensed image copies are not automatically imported into a new database. The public catalogue follows the separate reference-listing boundary in [architecture](architecture.md); newly added staff stock is not automatically published. An empty public catalogue also leaves the temporary demo unavailable until public reference listings exist. Reproducing application behaviour does not mean duplicating the owner's records.

### 4. Import the development project into Vercel

At [Vercel New Project](https://vercel.com/new), import your repository and select the repository root, FastAPI and Node.js 24. Keep the committed `vercel.json` build command (`python -m scripts.build_vercel`) and default FastAPI output handling; do not select `frontend/` as the root or add a wildcard API rewrite. Python's entry point is root `app.py`.

Create a project such as dealer-desk-dev. In its **Settings → Environments → Production → Branch Tracking**, select `main`. Enable system environment variables so the build receives `VERCEL_GIT_COMMIT_SHA`. In **Settings → Environment Variables**, set server-side `DATABASE_URL` to the development branch's pooled TLS connection, scoped to this project's Production environment. The project's name describes its application purpose; Vercel's Development scope is for local Vercel development, not this hosted main-branch project.

Keep development access protected. Deploy the successful main SHA. The build waits for that exact revision's trusted CI before building. A gate timeout is a failed build, not permission to bypass verification; redeploy after CI completes. Environment-variable changes require a new deployment. [Vercel Git deployment/branch settings](https://vercel.com/docs/git#customizing-the-production-branch) and [environment variables](https://vercel.com/docs/environment-variables) describe the provider controls.

### 5. Create the manually released production project

After reviewing main CI and the development smoke checks, run this in your fork's checkout, replacing FULL_VERIFIED_SHA with the actual 40-character revision:

```sh
uv run python -m scripts.promote FULL_VERIFIED_SHA
```

This creates or advances the remote `production-release` branch without force. Create a separate Vercel project for production using the same repository. Before attaching its production database, set **Settings → Environments → Production → Branch Tracking** to `production-release`. If the import initially built main, do not treat that build as the production release; select/build the verified production-release reference after the settings are saved.

Set this project's Production-scoped `DATABASE_URL` to the separate production Neon endpoint. Do not assign the production connection to unrelated Preview builds. Verify the role/schema using the intended production database and deploy the selected reference. This project currently uses one provisioned database role per target; separately provisioned least-privilege runtime and migration roles are not claimed.

For a public showroom, choose the intended production access setting while retaining preview protection and individual staff app login. App authentication must remain enabled. The original project's public alias uses Standard Protection; a Vercel access wall and the application's staff login are different controls.

| Application purpose | Vercel production branch | Database endpoint | DATABASE_URL scope |
|---|---|---|---|
| Development project | main | Development Neon branch | Production in the development project |
| Production project | production-release | Separate production Neon branch | Production in the production project |

Future main pushes deliver development automatically after successful CI. Production changes only when an operator promotes a reviewed SHA. No new hosting or database settings are required for an ordinary compatible code-only release.

### 6. Check the running copy

Check your own generated deployment URL, not the original project's address:

| Check | Expected result |
|---|---|
| `/` | 200 and the styled homepage |
| `/health` | `status: ok` and the selected full revision |
| `/api/catalogue` without a staff cookie | 200; it can be empty in a fresh database |
| `/api/vehicles`, `/api/enquiries`, `/api/tasks` without a staff cookie | 401 |
| Manager sign-in | Your newly provisioned account works |
| Staff workflow | Create vehicle → linked enquiry → follow-up; reload and confirm the records persist |
| Enquiry attention | Completing a task leaves its open enquiry visible until staff explicitly closes it |

Record the source SHA, CI run and deployment identity. Keep secrets and customer data out of the receipt. Retained evidence for the original setup is in [verification](verification.md); it is not proof that your new copy has passed. Use [release/recovery](release-recovery.md) for compatible rollback and independent restore checks.

## Build and runtime

Use the repository root and [FastAPI framework](https://vercel.com/docs/frameworks/backend/fastapi). app.py exports the ASGI application; vercel.json invokes `python -m scripts.build_vercel`. That command waits for trusted successful main CI at the exact source SHA before installing/building the frontend, then copies generated frontend/dist files to public/. Vercel serves those generated assets; hash routes need no wildcard rewrite that could capture /api.

Python 3.12 and Node.js 24 are the selected runtime/build targets. A local build can use `uv run python -m scripts.build_vercel`; the CI guard activates in Vercel. The guard/build never connects to or migrates a database.

.vercelignore excludes runtime data, environment files, tests, unrelated docs and reference originals. Approved public article Markdown and screenshot assets enter the frontend build; only generated assets are copied to public/. Photo bytes/credits required by the interface are served through the API/database. Server connection strings are not frontend environment variables.

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

## Customer workflow release switches — 27 October 2026

The newer customer/enquiry/lead migrations and public_write_windows table must be migrated explicitly before enabling the new release. PUBLIC_ENQUIRIES_ENABLED=true in the project environment enables bounded website enquiries and email-preference withdrawal; otherwise these hosted writes fail closed. Limits use atomic SQL windows shared across Vercel instances, rather than process memory. Customer registration/recovery remains disabled on hosted deployments until a real verification-delivery integration is configured; local email previews must never be exposed publicly. The public capabilities route reports this and the account screen hides unavailable registration/recovery controls. The saved customer/staff demo works independently in the browser.
