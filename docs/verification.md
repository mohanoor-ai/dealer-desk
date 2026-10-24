# Verification record — first persistent journey, 22 October 2026

This records actual checks, not inherited claims. Source is a new isolated project based on inspected local models, migrations and frontend scaffold. F:\AiProjects\dealer-stock-enquiry-tracker remains unchanged. No remote repository was pushed and no public deployment was created.

## Checks passed
- Backend: 13 pytest tests, including individual login/logout, cookie flags, revoked/expired sessions, viewer write denial, cross-site mutation denial, local login throttling, linked persistent workflow, simultaneous revision conflict, validation, workflow/date rules, literal search/pagination, change feed, actor audit and the committed API contract matching the implementation.
- Frontend: 4 Vitest tests, covering exact money, central client session/header/204/conflict behavior, invalid sign-in message and read-only empty state.
- TypeScript compilation and Vite production build passed.
- Browser against real SQLite API: individual login, create Demo Motors City at £12,995, record Fictional Buyer enquiry, schedule 24 October follow-up, complete it, reload. Records and completed state remained. Screenshot: evidence/journey-desktop.png. No mocked API used.
- Responsive check at 390 × 844: DOM reported no horizontal overflow (document width 375, viewport 390). Screenshot retained in evidence/journey-mobile.png. This is a basic breakpoint check, not a full accessibility audit.
- Docker multi-stage image built using Node 24 and Python 3.12 official base images and locked dependencies. Runtime is non-root.
- Dedicated Compose project dealer-desk-audit-20261022: real Postgres 16 and app on loopback port 8098. Login, stock, linked enquiry/task, completion, stale conflict, audit count and served frontend passed via real HTTP.
- Replaced only the dedicated application container. Account, stock price and completed task remained in PostgreSQL. Database volume retained.

## Commands used
Python tests ran with the audit copy's already installed locked environment from the new application root:

```text
../../work/existing-dealer-audit/.venv/Scripts/python.exe -m pytest tests -q --basetemp ../../work/pytest-journey-01 -o faulthandler_timeout=20
cd frontend
npm run build
npm test
```

Container verification used `docker compose --project-name dealer-desk-audit-20261022 --env-file <private-work-fixture> up --build -d` and a separate synthetic HTTP smoke script. Fixture passwords and databases remain under work or the dedicated Docker volume. The scripts and automated suites are being consolidated for clean-checkout verification; these paths are verification-session details, not the end-user setup instructions.

## Warnings and limits
- Starlette emits a TestClient/httpx deprecation warning. Tests still pass; dependency compatibility should be addressed before a final release.
- SQLite migration and real PostgreSQL startup upgrade passed. Migration downgrade and backup/restore are not yet exercised in this new project.
- Start scripts have been written. The full interactive first-run path on both Windows and Linux has not yet been verified; Docker build and Compose deployment were verified directly.
- CI workflow is written but has not run on GitHub. It tests and builds; no CD step is claimed.
- Local login limiter is process-local. Distributed rate limiting, public abuse controls, request-size quotas and session housekeeping remain required before public deployment.
- No public URL, hosted CI/CD, telemetry UI, alert-triggered agent fix, complete security scan or final rubric completion is claimed.
- Import/export, backup/restore, archive/audit interface controls, full learning companion and optional AI remain planned.
- The live preview at port 8097 uses a separate private-work SQLite database and fictional local test account. That account does not ship in source or create a public credential.

## AI-use record for this change
User asked to continue after approving beginner scope and audit. The assistant inspected the target contract/spec and existing models, then implemented account/session helpers, validation, routes, revision transaction/audit, real frontend connection and startup packaging. Review identified startup readiness as a race; Compose health checks and wait were added. A container smoke run initially reached its final success message but failed printing a Unicode arrow under Windows cp1252; the message was changed to ASCII and the complete smoke check reran successfully. No model was used inside the application. Learner explanation/reproduction and independent reviewer sign-off remain outstanding.

## Car pages and photos — 23 October 2026
Implemented separate overview, stock, vehicle detail, add-vehicle, enquiry and follow-up screens. Stock supports search/filter/sort; details include licensed reference photos, captions, credit links and gallery navigation. Staff can select multiple JPEG/PNG/WebP images and choose a cover, with revision checks and a 12-image limit. Uploaded images are bounded, decoded, resized and stripped of metadata; viewers cannot mutate them.

Resumed after computer shutdown: 19 backend tests passed (one existing Starlette/httpx deprecation warning), 4 frontend tests passed, TypeScript and Vite production build passed. OpenAPI regenerated and locked runtime requirements exported. Backend tests cover image persistence through a new app/engine on SQLite, upload validation, rights confirmation, metadata stripping, quota, conflict handling, cover selection and role boundaries.

The local preview restarted successfully on 127.0.0.1:8097 using the existing private SQLite fixture. Earlier visual inspection showed the ten reference images on the stock cards and the Ford detail page. The browser's URL policy rejected access after restart, so no new interactive upload or responsive verification is claimed. PostgreSQL photo persistence and a new Docker build remain pending; earlier PostgreSQL evidence predates this photo extension. No public deployment is claimed.

## Release preparation — 24 October 2026
Vercel FastAPI entrypoint, explicit frontend build, Python version, static-response headers and upload exclusions added. Hosted database configuration now requires PostgreSQL/TLS, normalizes the psycopg driver and uses NullPool with a connection timeout. Hosted login cookies are always Secure. No migrations occur at build/import; the runbook describes a serialized separate migration stage. Product-facing educational copy was replaced with neutral dealership wording.

Checks actually run:
- Full backend suite on SQLite: 26 passed, one existing Starlette/httpx deprecation warning.
- Real PostgreSQL 16 regression: 18 auth, journey and photo tests passed. Disposable loopback-only dealer_test instance; unique per-test schemas, migrated and cleaned by the fixture. Photo and core journey data survived new application/engine instances.
- Frontend: 4 tests passed; TypeScript/Vite build passed. Exact python -m scripts.build_vercel command completed successfully, installing locked dependencies and generating public assets.
- npm audit initially found vulnerable transitive undici 8.11.2 under jsdom. Updated compatibly to the patched release recorded in package-lock.json; npm audit then reported zero known vulnerabilities. This is an npm dependency check, not a full security certification.
- Source/history scanner checked 90 source files and two reachable commits, with zero remaining findings under its limited rules. The initial Compose finding was the literal ${POSTGRES_PASSWORD} reference, reviewed and handled with an exact exception. No credential value is printed by the scanner. Git diff whitespace check passed.
- CI now includes a PostgreSQL service/regression step and source/history check. No hosted workflow execution is claimed.

Vercel project connection, a hosted build, Neon migration, R2 storage, shared rate limiting, demo isolation, hosted telemetry and public-release checks remain pending. The prepared development deployment must stay protected by Vercel Authentication. No repository was published and no hosting resource was provisioned during this step.

Current Docker image dealer-desk:release-prep-20261024 built successfully after the photo/runtime/dependency changes. This verifies the build only; current-image Compose startup/container replacement and hosted deployment remain separate checks.

## Hosted source and CI — 24 October 2026
Published the reviewed application source and three local commits to the new public repository https://github.com/mohanoor-ai/dealer-desk. The existing dealer-stock-enquiry-tracker repository was not modified. Remote main was verified at cd525a979ceeccdbab0d5c20c06d945cefd3eb20.

First hosted GitHub Actions run passed: https://github.com/mohanoor-ai/dealer-desk/actions/runs/40097931885 (job 120883987554). Confirmed successful locked installs, source/history audit, backend SQLite tests, PostgreSQL regression, frontend tests/build, Docker build and API artifact upload. This is CI evidence for commit cd525a9; it is not CD or a deployed application URL.

Public acceptance-criteria tracker: issues/1 (Vercel/Neon development deployment), issues/2 (R2), issues/3 (showroom/demo linkage), issues/4 (delivery and operations evidence). The assistant created these from the agreed plan and is using issue 1 for the next deployment work. No closed issue or completed hosting claim is implied.

## Hosting account preparation — 24 October 2026
Vercel's GitHub App installation was explicitly approved by the owner and installed for only mohanoor-ai/dealer-desk. The Vercel import form detects FastAPI from vercel.json and the build command python -m scripts.build_vercel at root ./; the proposed project name is dealer-desk-dev. No Vercel project or deployed URL is claimed yet.

A dedicated Neon Free project dealer-desk-dev was created in AWS Europe West 2 (London), with database dealer_desk_dev on PostgreSQL 16. The console confirms Free plan and version 16. Its default branch is named production by Neon; it belongs to this dedicated development project and does not contain dealership business data. No migration or application connection has yet been performed. Connection-secret transfer is awaiting explicit owner approval; no credential is recorded here.

An attempted team-wide Vercel default-protection save was rejected by automatic approval review as broader than the authorised project scope. It was not saved, and the unsaved settings tab was closed. Use project-specific protection for Dealer Desk; do not change team defaults as a workaround. Vercel's 9 September 2026 changelog says All Deployments authentication is now available on every plan; verify the exact project setting and signed-out behaviour before relying on it: https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan

## Protected Vercel deployment and Neon journey — 24 October 2026
The connection secret was transferred with explicit owner approval directly into Vercel's server-side DATABASE_URL and a private local migration file outside Git. No credential was displayed or committed. Alembic migration on the dedicated Neon development database passed at 20261022_photos; the initial vehicle count was zero.

Vercel project: dealer-desk-dev, Hobby workspace Mo. Dashboard: https://vercel.com/mo-5996/dealer-desk-dev. Hosted address: https://dealer-desk-dev.vercel.app/. Initial deployment 7P8o9CgjeAyUwnkbZnUbDSdSuxyG reported Ready for source 71d4bdc199d5e34b7383d1240066bc863d9a6489.

Project-specific Vercel Authentication was set to All Deployments, saved and confirmed after a fresh settings reload. No team default was changed. Anonymous HTTP requests without cookies or bypass secrets to /, /health and /api/vehicles each returned 302 to the authentication flow. In the authorised browser, /health returned status ok and version 0.4.0, proving the deployed API reached its migrated database.

Hosted browser journey using a temporary random-credential sales test identity: login succeeded; a clearly labelled synthetic vehicle was created; two copies of the same licensed Ford image uploaded in one batch (explicit duplicate-test caption and retained Vauxford/CC BY-SA attribution); cover selection was exercised; a fictional enquiry and follow-up were saved; completing the follow-up produced zero open follow-ups after page reload. The duplicate files are test fixtures, not distinct vehicle angles. No real customer information was used.

This is a protected development deployment, not the public customer showroom. R2 storage, independent release environment, customer/demo isolation, shared login limits, gated CD and operational evidence remain incomplete. The existing local car inventory has not been copied into this new hosted database. Automatic Vercel Git deployment currently runs independently of GitHub CI; CI-gated delivery/manual release promotion is still pending.

Redeployment verification: pushing the documentation commit cfead5af2503ded29a0c74b174413c1e169e3fc8 triggered a new Vercel deployment FKbxw91Si3jFnZsZeJmfshkrxuMH, confirmed Ready in the dashboard. A fresh hosted page load retained the signed-in test session, synthetic vehicle, two images, second-image cover and linked enquiry. Task completion had previously persisted through a page reload. The temporary sales identity was then disabled and all of its sessions revoked. A local owner-run manager-account helper was prepared outside the repository; it prompts for a password without displaying it. It was syntax checked but no owner account was created by the assistant.

## Owner account setup — 24 October 2026
The owner reported creating the manager password through the prepared setup process. This is owner-reported account setup, not independent verification of a successful hosted manager login. Do not record any password, password hash, connection string or account database in this repository. Manager sign-in confirmation remains pending; the earlier hosted sales-account journey was independently verified and its temporary identity was disabled afterward.
