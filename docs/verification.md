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
