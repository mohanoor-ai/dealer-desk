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

## Browser demo implementation — 24 October 2026
Owner has confirmed manager login works (user-reported; no password collected). Frontend: npm test passed 9 tests, including no network writes, customer mutation denial, reset isolation, expiry without fallback, bounded records, disabled photo upload, and rendered customer enquiry/end flow. npm run build passed TypeScript and Vite. jsdom reports its unimplemented scrollTo during navigation; assertions pass. No database schema or backend auth changes. Hosted demo verification and public access approval remain pending; do not describe this as live multi-user integration.

## Hosted browser checks and cache fix — 24 October
Found stale cached root HTML referring to removed index-DxdErHc9.js (404), despite Ready deployment. A release-query URL loaded the current build correctly. Added no-store for HTML in backend middleware and root/index routes at Vercel CDN; hosting regression checks both layers. Hosting tests: 8 passed; frontend: 9 passed including customer detail navigation and selected enquiry vehicle; TypeScript/Vite build passed. Browser on 5ea7bd0: customer demo fictional enquiry saved locally, switching to dealer cleared linked enquiries, Ford sample status changed available to reserved and revision 1 to 2. No dealership mutation was performed. New cache-fix release hosted validation pending.

Release 1695e17: Vercel Ready and GitHub CI succeeded (run 40128827104). Hosted customer view opens Nissan Qashqai with the matching enquiry selection. Saved screenshot outside repository at outputs/temporary-customer-demo-verified.png. Older cached root still referenced its removed bundle, so added a narrowly matched missing-bundle recovery route with a same-release guard against loops. Full backend suite: 27 passed; existing httpx deprecation warning remains. Recovery hosted check pending.

Hosted visual check caught CSS being intercepted by the asset route (unstyled page). Fixed the route to serve current hashed CSS with text/css, while missing CSS remains 404 and only missing JS runs recovery. Hosting regression now covers current JS, current CSS, unknown filenames and missing CSS: 8 passed. Final styled-browser proof pending this corrective deployment.

## Front-page visual documentation — 24 October
Captured the actual protected hosted staff Overview from application baseline b01d3427787b6abb70eae16ba8656ce104a2457b. Public main and Vercel success status matched that baseline before capture. Image contains only the existing fictional test workspace: one vehicle, one open enquiry, zero open follow-ups. No records, counts or UI were edited for the capture. Retained Vauxford reference-photo attribution in docs/media/README.md. Added current architecture/journey diagrams to README and detailed current/planned release and incident diagrams in docs/diagrams.md. Renamed the learning/course heading to engineering documentation and verification. Agreed documentation rules are linked from AGENTS.md. Source/history scan checked 96 source files and 12 reachable commits with zero findings under its limited rules; whitespace check passed. These are documentation changes; no app runtime changes or new test runs are claimed. Rendered GitHub diagram verification follows publication.

Published README image loaded successfully on GitHub, and both Mermaid diagrams rendered their expected labels without an error. Visual inspection found the initial horizontal layout too small at the current browser width; switched front-page diagrams and longer delivery flows to a vertical layout for readability. Private companion map/links are verified separately outside this repository.

## Project description and article preparation — 24 October
Added a plain project description, GitHub handle attribution, protected app access wording, project overview and bottom README Learning in public index. Three article drafts and a submission draft are private sibling deliverables; no full name, personal reflection or publication was invented. Repository About description and website were saved through GitHub. Documentation-only change; no application tests repeated. git diff --check passed. Final rendered README and About verification recorded separately.

## Confirmed author credit
Owner supplied Mohammed Sheikh-Noor. Updated README, project overview and article index; private submission/article drafts match. GitHub URLs preserved. git diff --check passed; no runtime change or app test rerun.

## Submission evidence check — 25 October 2026
Official current rubric rechecked at de41e4096d8ac08db3852dfda4ce802f9ac0c0d2: twelve criteria, 24 points, ten-point threshold and three compulsory peer reviews. Public form requires public GitHub URL and exact commit; hosted credentials are not a form requirement. Added modular team/process/testing/security/AI-use documentation and a criterion-by-criterion evidence index; corrected stale unselected-hosting and unreviewed-source statements. No independent specialist review or historical handoffs invented.
Ran .venv/Scripts/python.exe -m scripts.verify: backend 27 passed (one existing FastAPI/httpx deprecation warning); frontend 9 passed (jsdom scrollTo notices); TypeScript/Vite build passed; limited source/history audit checked 106 files and 16 commits with zero findings. Retained actual output in docs/evidence/submission-core-checks.txt. It reflects the working tree at scan enumeration; later documentation additions are checked separately before publication. CI now runs the same verification entry point with pipefail and retains output even on failure; PostgreSQL regression and Docker build remain separate CI steps.
Fresh Docker engine check did not complete and was stopped; no fresh Compose success claimed and no data/volumes removed. Existing container/hosted evidence remains historical. CI-gated deployment/manual promotion/rollback, correlated telemetry UI, user-impact alert, on-call repair and extension pack remain incomplete. This is a submission-evidence update, not a claim of maximum assessment completion.

Final pre-publication source/history scan: 108 files, 16 reachable commits, zero findings under the documented limited rules; docs/evidence/submission-source-audit.txt retains output. Local Markdown path check: 22 references, zero missing. Workflow YAML parsed; hosted execution of the revised CI follows publication.

## Operations implementation and local verification — 25 October 2026
Added opt-in OpenTelemetry SDK traces, metrics and logs using local OTLP/protobuf export; a bounded loopback SQLite collector and read-only correlation UI; a three-failure authenticated-stock alert and fixed-action deterministic response agent; independent backup/restore lab; stdio MCP aggregate tool, reusable procedure, specialist definition and enforced repair permissions. No independent specialist or LLM invocation claimed. The initial rehearsal failed because it targeted an unversioned table name; corrected it to vehicles_v2 and preserved the failed fixture locally.
Actual incident: three 503 stock reads triggered automatic table diagnosis/restore, followed by 200 and preserved vehicle. Actual independent restored backup matched count and integrity_check=ok. Screenshot operations-correlation.png shows real stored trace/log/metric-exemplar joins. Initial working-tree signals were based on 3298b5f with uncommitted operations code, so that resource version must not be treated as an immutable artifact; CI reruns against its own checkout.
New tests verify real OTLP collection and all-three-signal correlation, invalid payload handling, endpoint/credential restrictions, policy denials/data preservation, real MCP protocol discovery/read and unknown-write denial, and exact-commit CI gate rejections. Full core suite passed 36 backend tests, 9 frontend tests, TypeScript/Vite build and limited audit: 136 source files/17 reachable commits, zero findings. Output: operations-core-checks.txt. Audit optimization caches path/blob results while retaining a finding for every affected revision, with a regression proving both history coverage and redacted output.
The CI workflow now includes clean Compose/HTTP journey/container replacement, previous-image rollback/forward recovery, real incident and backup labs. Execution evidence follows publication; these workflow definitions alone are not passing-run evidence. Local Docker restart did not restore the Linux engine. A second-browser native Chrome approval timed out; no independent two-browser success claimed. Existing concurrent API-client verification remains separate.
Release gate unit tests passed and an actual GitHub lookup confirmed successful CI for revision 3298b5f. The Vercel build guard now fails closed until trusted exact-revision CI succeeds. Hosted gating verification, separate manual production environment and cloud rollback remain pending. No new production project or Neon branch has been created.

Final operations pre-publication check: limited scan 137 files/17 reachable commits, zero findings; 28 local Markdown paths resolve; Python sources compile and CI YAML parses. See operations-source-audit.txt. Await hosted clean Compose, rollback and lab execution before claiming those checks passed.

Hosted CI e51d7d7: https://github.com/mohanoor-ai/dealer-desk/actions/runs/40174651942 completed successfully, including PostgreSQL regression, clean Compose HTTP journey, app replacement, previous-image rollback, forward recovery, actual incident and independent restore. Vercel deployment 6pHdNYKEJ1N5vgkkHW8Kv57NWXt1 became Ready for e51d7d7; its visible build log recorded 'Trusted CI passed for exact revision e51d7d7b6610062af1731a2aefcefa92f86404a5' before frontend build. Hosted protected /health returned status ok/version 0.4.0. Screenshot vercel-ci-gate.png retains the actual line.
Manual independent browser-session check: browser-a at 127.0.0.1 and browser-b at localhost used distinct host-scoped cookies against the same rehearsal database. A opened revision 1; B reserved the vehicle at revision 2; A's stale price edit was rejected with the visible refresh message. After reload, revision 2 and original price remained. B changed status again; A observed revision 3 without reload through normal polling. Both signed out; their synthetic identities were disabled and sessions revoked. Screenshots two-session-conflict.png and two-session-shared-stock.png contain fictional records only. This is a manual two-session check, not a cross-engine automated suite.
Owner authorized the separate protected production copy and isolated Neon branch on 25 October. Branch dealer-desk-prod (br-restless-flower-za6p5fmd) was created in the existing Free-plan project, with auto-delete Never. It cloned the existing synthetic development snapshot; its connection is retained privately outside Git, migrations are at 20261022_photos, and one copied session was revoked on the new branch only. Production-release branch was created at tested e51d7d7. Production Vercel project configuration and manual promotion/rollback verification are in progress.

Dependency review found Certifi 2026.7.22 affected by PYSEC-2026-4320 / GHSA-6q48-6c7w-9gw2. Preserved the actual pre-fix report in security/dependency-audit-before.json; upgraded the lock and exported runtime requirements to Certifi 2026.10.23. Repeated PyPA audit reported no known vulnerabilities for the scanned pinned runtime set. security/review.md records scope, finding, disposition and remaining limits; no dependency advisory was suppressed. Production will first use a security-fixed revision; older vulnerable code is not a proposed production rollback target.

The post-fix core suite passed again: 36 backend tests, 9 frontend tests, production build and limited scan (148 files/18 commits). Runtime audit covered 35 packages with zero known findings after the Certifi update; a separate audit of the actual development environment, including the MCP toolchain, also reported no known vulnerabilities. These are time-bounded advisory checks, not a security guarantee. The release guard now accepts only trusted main-branch push CI; its targeted tests and a real e51d7d7 lookup passed. CI runs on main pushes and all pull requests; production-release reuses the verified identical main revision.
