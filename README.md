# Dealer Desk

A working educational application for one dealership: vehicle stock, enquiries and follow-up tasks in a shared persistent workspace. Each staff member signs in individually. Viewers can read; sales staff can update workflows; managers can inspect the audit history.

## Start with Docker
Install Docker Desktop on Windows (Linux containers) or Docker Engine with Compose on Linux. First setup downloads container images and dependencies and therefore needs internet.

Windows PowerShell: `./start.ps1`

Linux: `sh start.sh`

The script preserves an existing .env and database volume, builds and starts the app/database, and asks you to create the first manager account only if there are no users. Use a password of at least 12 characters. Open the browser address printed by the script. Subsequent runs preserve records and users. Never run `docker compose down -v` against data you need.

Create another account: `docker compose exec app python -m scripts.create_user alex --role sales`. Choose viewer, sales or manager. Passwords are entered interactively, never as command-line arguments.

## Local developer setup
Python 3.12+, uv and Node 24 are needed. From this folder:

```sh
uv sync --frozen
cd frontend
npm ci
npm run build
cd ..
uv run alembic upgrade head
uv run python -m scripts.create_user manager --role manager
uv run python start.py
```

Local development defaults to SQLite at data/dealer-v2.sqlite3. Set DATABASE_URL to use PostgreSQL. The frontend development server proxies /api to port 8090; start it with `npm run dev` inside frontend. The built interface is served by FastAPI.

## What works in the first milestone
- Login, logout, expiring/revocable sessions and server-enforced viewer/sales/manager roles.
- Create, read, search, filter and edit vehicles; vehicle status changes.
- Enquiries linked to stock, enquiry status changes, follow-up creation/completion/reopening.
- Persistent data and dashboard totals; shared views refresh every three seconds.
- Atomic revision checks reject conflicting edits; every material mutation records actor, record ID and revision in the audit table.
- Validated API inputs, centralized browser client and helpful empty/error states.

The API also supports archive/restore and manager audit queries; dedicated interface controls for these remain to be completed. Import/export, backup/restore, cloud deployment, hosted CI/CD, full operations evidence and optional AI are not completed in this milestone.

## Tests
`uv run python -m pytest tests` runs authentication and real SQLite integration tests. From frontend: `npm test` and `npm run build`. Current evidence and limitations are in docs/verification.md. These tests do not substitute for a PostgreSQL/browser/container check.

## Access and privacy
This is an educational demonstration. Use fictional records only. No fixed user or password ships with the app. Keep .env, database files, backups and exports private. The private learning companion is a sibling deliverable and must not be added to this public source folder.

localhost / 127.0.0.1 means this computer. The Compose port binding deliberately limits access to this computer; LAN access needs deliberate binding/firewall changes and HTTPS/authentication review. A public cloud URL is different: anyone can reach the login screen.

## Deployment direction
Target: Vercel hosting with external PostgreSQL, subject to the completed free-tier and security review. Set COOKIE_SECURE=true for HTTPS. Vercel Hobby permits personal non-commercial use; a real business deployment needs suitable terms. No public deployment is claimed here.

## Learning and course evidence
Read docs/architecture.md for technology choices, docs/tasks.md for acceptance criteria and docs/verification.md for actual results. The original contract design is retained as docs/prior-api-design.yaml; openapi.yaml describes the current implementation. An in-app LLM is optional and is not required by the inspected current final rubric.
