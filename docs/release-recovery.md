# Release controls and recovery

## Development build gate

Vercel builds call scripts/build_vercel.py. In Vercel, before frontend installation/build, scripts/release_gate.py requires a full VERCEL_GIT_COMMIT_SHA and checks the public GitHub Actions workflow for that exact revision. Only the latest push run of .github/workflows/ci.yml from mohanoor-ai/dealer-desk with completed/success passes. Missing revision, wrong origin/workflow, failed/cancelled/pending checks and unavailable GitHub fail closed. The guard never accesses the database.

The CI Docker build uses the Dockerfile directly and does not call the Vercel build entry point, so there is no dependency cycle. A deployment may start building before CI finishes, but cannot proceed past this gate until the trusted run succeeds. It waits a bounded time and fails if CI remains unfinished. A fresh redeployment may be needed after a timeout; the previous working deployment remains available.

tests/test_release_gate.py checks denial for wrong commit, workflow, fork, event, rerun failure, cancellation and pending state. Successful unit tests are not proof of a deployed gate: actual Vercel deployment verification must be recorded separately.

## Container recovery rehearsal

The CI workflow starts the application and PostgreSQL using Compose in a dedicated dealer-rehearsal project with a generated password. A synthetic identity creates vehicle/enquiry/follow-up records through HTTP. A private temporary cookie file is copied between replacement containers and never uploaded. The app is recreated, and the journey is read again to prove database persistence.

Next CI builds the previous Git revision into the app image, starts its API directly against the same disposable rehearsal database and verifies the saved journey. The rollback Compose override bypasses only the old startup migration command: an older Alembic graph cannot resolve a newer additive revision. It neither downgrades the database nor changes the previous application code. Forward recovery restores the current image with its normal migration startup. It then restores the current image and verifies again. Only the smoke verification helper is copied into the previous container; its application code remains the previous image. This tests compatible code rollback and forward recovery, not rollback of a destructive schema migration. Actual output is retained as container-verification.txt and rollback-verification.txt workflow artifacts.

## Manual production release

The operator selects a full reviewed revision and runs `uv run python -m scripts.promote <revision>`. This checks trusted exact-revision CI, verifies the local commit exists, and advances production-release without force. The production project deploys that branch; development remains on main. This explicit action uses the operator's existing Git permissions and needs no extra deployment token. Check health/staff workflow after deployment.

## Production boundary

The owner authorized a separate protected production project and isolated Neon branch on 25 October. The protected project and isolated branch are configured. Security-fixed release 5fc3aae passed its hosted journey; 30dad17 was then promoted after successful main CI. An actual Instant Rollback to 5fc3aae and Promote restoration to 30dad17 both returned healthy responses and retained the completed synthetic follow-up. See evidence/cloud-recovery.json, evidence/database-isolation.json and verification.md. The owner subsequently made production browsing public under Standard Protection; development/previews and app staff authentication remain protected. Do not promote a release with unreviewed migrations, missing smoke evidence or incompatible database changes.

Cloud operator checklist: verify exact CI revision, identify immutable deployment, inspect dev smoke evidence, manually select the approved production release, verify health revision and authenticated staff journey, and retain deployment IDs and results. Roll back only to a compatible known-good image; restore data separately into an isolated database before any deliberate cutover. Code rollback does not undo database writes.

## Registration without email verification

The owner-approved optional CUSTOMER_REGISTRATION_UNVERIFIED=true setting enables customer signup and sign-in without claiming email ownership. New accounts retain verified=false. Only enquiries submitted while authenticated are attached to these accounts; matching email never grants earlier guest conversations. Hosted verification previews and password reset remain disabled. Registration and login use shared database request budgets. Configure this setting only on the intended hosted project after schema migration and exact-commit CI. This does not send email or enable email-based account recovery.

## Pinned isolated rehearsal — 27 October 2026

The audit replaces implicit HEAD^ with explicit prior application `0efadbc32abcd7e372f59f4f03f9a080f1068d1f` (development release, successful CI 40431088971). It predates unverified-account sign-in semantics while already supporting the complete additive schema through `20261027_public_writes`. Baseline current application is c3bcfee; the audit source contains the extended helper and workflow. CI writes its exact checkout SHA, prior SHA and expected schema to rollback-revisions.txt. It does not claim the prior image offers the new immediate signup behaviour.

The earlier production `6d2f11b` is not selected as a generally compatible target: it predates nullable general enquiries and newer response shapes. A safe rollback target must be chosen by supported data/workflow compatibility, not just age or branch ancestry.

Current creation stores a legacy vehicle/enquiry/completed task plus an authenticated unverified customer, general enquiry, two conversation messages, linked ownership and explicit marketing preference history. Private cookies/IDs/fingerprints live only in the runner's chmod-600 state file, which is never an artifact. Artifact output contains aggregate results/record IDs and no credentials, addresses or message text.

The prior image starts its unchanged API directly, without running its older Alembic graph. The copied helper verifies legacy reads and a stock edit, and hashes the newer customer/session/message/preference tables and enquiry extension fields before/after. No new application routes are copied into the old image. Forward restoration starts the current image normally, verifies customer ownership/messages/Leads plus anonymous denial and public-data privacy. Data is not downgraded; this is an isolated compatible-code rehearsal, not a production rollback instruction.

A dedicated docker-compose.rehearsal.yml enables unverified registration only for the disposable CI project. Ordinary Compose startup is unchanged. Local process tests exercise the actual pinned old application and restored current application against disposable SQLite; a separate loopback test runs the helper across app replacement and confirms preference tampering fails its fingerprint check. Neither is claimed as Docker/PostgreSQL container evidence. The new container workflow remains pending because Docker was unavailable locally and pushing would trigger deployments forbidden for this audit.
