# Task tracker

Public tracker: https://github.com/mohanoor-ai/dealer-desk/issues. Issues 1–5 contain deployment, R2, showroom/demo, operations and enquiry-action acceptance criteria. Issues 1, 4 and 5 are closed with evidence; 2 and 3 retain deferred scope. See issue-traceability.md for the worked execution example. Historical entries below describe their dated checkpoints; later verified updates supersede earlier pending states. This table records the detailed local history; docs/verification.md records actual evidence.

| ID | Acceptance criteria | State |
|---|---|---|
| DEP01 | Vercel entrypoint and frontend build; no migrations at import/build; hosted startup rejects SQLite/missing TLS, secure cookies and bounded connections | Local checks and protected Vercel/Neon hosted journey verified; separate production release and cloud recovery verified; production browsing is now public with staff login retained |
| DEP02 | Tracked-source/history release audit, exclusion rules and deployment runbook; report blockers without claiming publication | Reviewed source published to new repository; private runtime files excluded |
| J01 | Operator creates individual user; valid login works; invalid login and viewer writes fail; logout revokes session | API and temporary hosted sales login verified; owner confirmed manager login works; later Overview capture used the staff session |
| J02 | Vehicle → enquiry → follow-up persists after app restart; completion updates dashboard | Verified on SQLite and PostgreSQL; browser reload verified |
| J03 | Stale edit returns 409 and does not overwrite; audit contains actor, ID and revision | Verified, including two simultaneous API edits |
| J04 | UI uses real API; usable loading/error/empty states; no product screen course jargon | Browser journey and basic responsive check passed; full accessibility review pending |
| J05 | Schema migrates on SQLite and PostgreSQL; clean Compose start and restart preserves data | Startup migrations, readiness and application-container replacement passed; clean interactive setup pending |
| J06 | Browser journey, roles, recovery and hosted CI/CD evidence | Hosted journey and CI verified; CI-gated CD, container recovery and protected cloud rollback/forward restoration verified |
| J07 | Current rubric operations/alert/responder evidence; safe extensions | Local OTLP collection/correlation, actual alert, bounded deterministic repair, backup lab and read-only MCP verified |
| J08 | Release archive, offline companion, public/private inventory and final submission | Source/companion packaging and final revision bundle prepared separately; owner submission and three peer reviews remain |
| UX01 | Separate overview, stock, enquiries, follow-ups and linkable vehicle-detail pages; browser Back works | Implemented; verification.md distinguishes completed local, PostgreSQL and browser checks from remaining test coverage |
| UX02 | Licensed stock illustrations with visible credits; no illustration represented as the actual stock vehicle | Implemented; verification.md distinguishes completed local, PostgreSQL and browser checks from remaining test coverage |
| UX03 | Staff can upload multiple JPEG/PNG/WebP photos, browse a gallery and choose a cover; viewers cannot upload | Implemented; verification.md distinguishes completed local, PostgreSQL and browser checks from remaining test coverage |
| UX04 | Photos survive restart on SQLite/PostgreSQL; size/type/dimension limits, EXIF stripping and conflict checks verified | Implemented; verification.md distinguishes completed local, PostgreSQL and browser checks from remaining test coverage |

## Temporary browser demo — 24 October
Acceptance: customer and dealer entry links; no registration or network business requests while demo is active; fictional per-tab data only; expire after 30 minutes; refresh/end/reset discard data; customer cannot change stock; bounded records and text; uploads disabled in this first sandbox; staff login unchanged. This is a browser simulation, not a shared live database integration. Public Vercel protection stays enabled.

## Hosted demo verification fixes — 24 October
Acceptance: prevent cached HTML referencing removed bundles by marking root/index documents no-store; test rendered HTML headers. Verify deployed customer enquiry, dealer stock/edit workflow and reset. Customer vehicle links must show the selected vehicle rather than repeat the catalogue. Preserve Vercel protection and staff permissions.

Cache recovery acceptance: an old cached HTML document requesting a removed hashed JavaScript bundle receives a bounded recovery script that loads the current release once. Existing assets remain served normally; unknown non-bundle paths stay 404; a missing asset on the same release must not loop. Test this before deployment.

## Front-page screenshots and diagrams — 24 October
Acceptance: README uses an actual staff Overview screenshot containing fictional data, dated and linked to its tested commit; no credentials/customer records or fabricated UI. Add editable Mermaid diagrams for current architecture and vehicle/enquiry/follow-up flow. Release/incident diagrams must be explicitly planned until implemented. Rename vague learning/course heading to engineering documentation. Private companion homepage gets a simple course-to-project map and module navigation; keep it out of app/public source. Retain source/verification notes and verify rendered pages and links.

## Project identity and article index — 24 October
Acceptance: plain project description, confirmed public GitHub handle as author, protected deployment link with accurate access instructions, repository About description/website, bottom README article index with status, three evidence-based drafts kept private pending owner review, and a private submission draft with outstanding requirements. No invented full name or personal reflection; no product/course UI changes.

## Confirmed author credit
Acceptance: use the owner-confirmed spelling Mohammed Sheikh-Noor in README, project overview, article index and private drafts; preserve GitHub URLs.

## Submission evidence completion — 25 October
Acceptance: recheck official current rubric and form; add modular team/process/testing/security and AI-use docs describing actual collaboration without invented handoffs; provide one fail-fast backend/frontend verification command; run checks and retain sanitized real output; reconcile stale status claims; keep protected hosting and private content separate; prepare exact revision and form fields. Operations and release capabilities must remain labelled incomplete unless actually demonstrated.

## Complete release and operations — 25 October
Acceptance: enforce CI-gated dev delivery and manual production promotion with immutable revision/smoke/rollback evidence; instrument the real stock journey with correlated redacted metrics/logs/traces, collected/stored/viewable in a local UI; demonstrate an actual user-impact alert and bounded alert-triggered repair in an isolated environment; add runnable extension workflow/tool/guardrail and permission tests; verify clean setup and two-browser persistence; retain real artifacts and reconcile all status documents. Never weaken hosted protection or use production data for fault injection.

## Site-wide interface — 25 October
Acceptance: approved warm white/forest green layout, original stencil DD logo and labelled flying-roadster concept hero; home, catalogue, vehicle detail, contact and separate staff sign-in; imported sample stock read through a bounded read-only catalogue with only sample vehicles and illustrative photos; staff endpoints remain authenticated; one discreet demo entry; compact/list stock controls; responsive shared typography/forms/navigation across existing staff pages. No new enquiry delivery, bulk upload, email or WhatsApp integration. Verify catalogue privacy boundaries, navigation and frontend build; capture actual rendered pages before release.

## Public production access — 25 October
Owner requested removal of the Vercel wall. Acceptance verified: production homepage/sample catalogue open without Vercel credentials; private stock/enquiry/task APIs require app login; previews and development retain protection. Actual no-cookie results recorded in verification.md.

## Issue 5 — actionable open enquiries
Acceptance: Open enquiries links to non-closed records; overview names customer/vehicle and displays actual enquiry text plus unscheduled/overdue/due-today/upcoming state; enquiry cards link existing incomplete tasks or preselect that enquiry in Schedule follow-up; completing the last task while enquiry stays open restores unscheduled state; closed enquiries excluded from attention. Preserve viewer restrictions and backend auth. Verify with regression tests and a real saved local workflow. Update issue/evidence and release; bulk upload and message integrations remain deferred.

Owner refinement: clicking the enquiry count opens open enquiries; clicking an individual enquiry number opens that exact enquiry from Overview, enquiry cards, vehicle-linked enquiries and follow-up tasks.

Owner wording refinement: ordinary example customer names/messages, no fictional/deployment labels in normal records; one site-level demonstration notice and reference-price/photo disclosures retained. Only known test fixtures renamed/relinked, unused operational test cars archived without deletion, and private before-images retained. Catalogue markers remain internal.

## Assessment documentation reconciliation — 25 October
Acceptance: README presents problem, expected behaviour, stack/platforms, setup/tests, AI-assisted process and evidence; product specification describes current behaviour and numbered acceptance criteria with deferred scope separate; architecture/process reflect public production and tested release/recovery; issue #5 traceability links owner report, execution, code, tests, CI and deployment; observability distinguishes the implemented local collector/UI from the taught Grafana/LGTM stack. Preserve dated verification history and screenshot provenance. Check links, wording consistency and source audit; no application, database or hosting change.

## README assessor reading order — 25 October
Owner-approved acceptance: Problem description contains The problem, System functionality and Expected system behaviour; distinguish customer website from staff/dealer workspace. Product specification appears early with concise acceptance criteria and linked detail. Observability is a short capability list with one full-details link. Use natural project headings and a short contents line; retain key verification results in README without rubric numbering or implied grades. Documentation-only change.

## README project evidence and issue summary — 25 October
Acceptance: add Project evidence with the twelve exact criterion titles, concise factual summaries and evidence links; no scores or course-labelled heading. Add a linked issue table that distinguishes GitHub open/closed state from implementation/deferred scope, based on current public tracker checks. Keep a full-list link and preserve existing reading order. Documentation-only.

## Final README consolidation — 25 October
Owner-approved acceptance: remove repeated Project evidence section; preserve unique context/CI/alert/responder details in existing sections; retain Product specification links and issue table/full-list link; remove Course alignment from operations.md; place the existing actual telemetry screenshot at the end of README with date, environment and accurate working-tree source qualification. Check links/rendering and refresh submission candidate. Documentation only.

## README landing image, technology and deployment — 25 October
Owner-approved acceptance: add an actual public landing-page screenshot directly beneath the project name with concise capture/source details; keep staff workflow screenshots separate. Explain each implemented technology’s role briefly. Add a distinct Deployment section after tests and before observability covering platforms, access, environment separation, CI gate/manual production, verification/recovery and a full runbook link. Preserve telemetry image at README end. Check links/rendering; documentation and image only.

## Logo, full-page collage and mobile navigation — 25 October
Acceptance: reuse the existing DD SVG identity in the GitHub README; replace the top-only landing image with a collage of actual full-page landing/catalogue/detail/staff screens, preserving individual originals and provenance. On narrow screens, replace scrolling top/bottom link rows with three-bar controls and vertical navigation; support customer/staff contexts, close/Escape/route changes, focus handling and safe-area spacing. Desktop navigation remains visible. Verify component behaviour, build, rendered captures and hosted release; no invented customer data or photo claims.

## Final rubric review — 25 October
Acceptance: re-read the current official twelve-criterion rubric and compare code, actual retained reports, trusted CI and public deployment. Verify alert-triggered deterministic repair and trace/log/metric correlation without replacing the responder or adding infrastructure. Clarify existing agent responsibilities and reviewer reproduction steps where evidence is incomplete. Run relevant tests and inspect final exact-revision CI. Keep unfinished website-article work in its named Git stash; no production promotion, configuration/data changes or new independent agents. Report justified score estimate and real limitations; preserve the existing saved submission unless explicitly updated.

## Publish fourteen website articles and update submission — 25 October
Owner-authorized acceptance: restore and finish fourteen distinct articles from the paused work; bundle readable Markdown sources and images with the app, use article URLs relative to its current origin, provide public index/detail/not-found pages and footer/mobile access, include #aidevtools and linked course references. Preserve the owner's removal of the README learning section. Validate factual statements and local links; test public access, all article routes, rendering, safe links and build/container compatibility. After exact-revision CI and authorized production promotion, verify actual hosted pages and update the saved submission to the final verified commit plus fourteen website article URLs. Retain the receipt privately; no claim of moderated points or social-platform notification.

Owner wording correction: remove Prepared with AI assistance and the project-progress/organization/instructor footer from every article and the index. Use one official course link instead; retain hashtags. Repository AI-use records remain separate. Verify before final release and submission update.

## Remove journal promotion from customer pages — 25 October
Owner acceptance: remove the homepage FROM THE PROJECT/Building Dealer Desk article block and public Learning in public footer/navigation entry. Preserve all fourteen direct article URLs and their submitted links; keep README unchanged. Run frontend checks and gated release, verify public rendering and retain the latest submission revision.

## Seed demos from current public listings — 25 October
Acceptance: fetch the public catalogue before a new customer/staff demo, copy only public vehicle fields and credited illustrative photos into per-tab memory, and remove the outdated hard-coded three-car seed. Reset restores the starting catalogue snapshot; ending and starting again refreshes it. Failure/empty catalogue must show an error without starting a stale demo. Keep demo mutations/enquiries/tasks/photo metadata in memory, no staff database reads/writes, and no network fallback for demo operations. Verify count/values, reset/isolation, public photos, failure handling and both hosted demo roles, then update the final submission revision.

## Author wording and README image proposal — 25 October
Owner acceptance: remove standalone AI-credit boilerplate from current descriptions while retaining truthful technical agent/workflow records, author Mohammed Sheikh-Noor and immutable Git history. Prepare a compact editable functionality infographic for review; do not replace the README front image until owner approval. Retain actual customer read-only and staff authenticated boundaries and do not imply live website enquiry delivery.

Owner approved the reduced 560px functionality diagram. Replace only the tall front collage with the linked SVG, retaining the logo, screenshot originals/collage links, workflow captures and final telemetry screenshot. Verify rendered GitHub layout and final exact-commit CI before aligning the submitted revision.

## Local/cloud running summary and deployment how-to — 25 October
Owner acceptance: link Vercel/Neon in README, summarize hosted and local running near the project introduction, and expand the existing runbook into actionable independent-account setup. Cover fork-specific trusted CI identity, private TLS connections, migration/account provisioning, separate dev/prod projects and branches, exact-revision release, smoke checks and empty-database limits. Keep cloud availability distinct from reproducibility. Documentation only; no new service, credential, database or production modification. Validate code/official-reference alignment, links and exact-commit CI, then align the submitted revision.

## Staff demo entry — 26 October 2026

Owner request: make read/write demo access clear and place entry under staff login. Acceptance: direct staff-demo button beneath sign-in; describe temporary vehicle/enquiry/follow-up edits, no account needed, reset on refresh/end; retain current isolated memory-only writes, current public catalogue bootstrap, expiry and photo-upload restrictions. No production promotion without approval.

## Local enquiry pipeline prototype — 26 October 2026

Owner-authorized local demo only. Acceptance: manually recorded enquiries require a source; website enquiries set Website automatically and validate name/email/message/vehicle; keep customer and staff views in one temporary session; source/contact details visible; reply uses encoded mailto and never marks sent on opening; explicit staff confirmation records immutable activity and Contacted state; follow-up links use existing tasks; closure records outcome and rejects pending tasks; reset/expiry clear all prototype records. Gate UI to explicit local build flag and loopback hostname. No production API/schema/database/deployment change. Test validation, role isolation, no business network writes, reply confirmation, closure and UI journey.

## Whole local enquiry workflow — 26 October 2026

Owner authorizes the agreed design across the local application, beyond the temporary demo. Acceptance: customer vehicle button opens accessible modal with fixed vehicle and explicit different/general option; bounded request categories/contact validation; public local submission persists with minimal receipt and replay protection; staff create source and optional follow-up atomically; staff replies and manual contact outcomes retain actor/time/activity and optional next action; closure requires outcome/no pending tasks; dashboard first for staff and demo, meaningful pipeline/due-work counts; viewer remains read-only. Schema migration preserves prior records. Customer API never returns private fields, accepts only published vehicles/general, bounds abuse locally. Temporary demo mirrors workflow without network business writes. No production deployment/migration/push/submission change. Update contract, tests and local verification.

## Customer continuity and persistent shared demo — 26 October 2026

Owner authorizes local implementation: receipt returns to selected car with viewed/browse links and no new-enquiry prompt; separate customer registration/login/verification/reset with private own-enquiry threads and verified-email guest linking; staff/customer messages reopen response attention and exclude internal notes; compare at most three real catalogue records, optional recently viewed storage, verified expert-review stars only; global Privacy/Cookies/Terms and honest storage controls. Shared persistent demo uses device-local storage for test records only, survives refresh and role changes, offers explicit reset/clear, and never writes to dealership database. Real customer records remain in SQL with hashed credentials/tokens and role/ownership checks. Local verification preview must be visibly distinguished from delivered email; hosted signup stays disabled without configured delivery/release review. No production, Neon, GitHub push or submission updates.

## Compact enquiry actions — 27 October 2026

Owner approved concise enquiry cards with one action selector (reply in account, email reply, contact, schedule follow-up, close); only selected fields visible; optional Add follow-up for reply/contact; current task summarized once; contact/conversation/activity collapsed; source/status/vehicle/request remain readable; viewer no write controls. Collapse manual recording until requested. Preserve email-send confirmation, atomic task creation, closure checks, saved demo and existing permissions. Local only. Verify selectors, hidden forms, schedule payload, combined replies and core checks; no production change.

## Required enquiry fields and leads — 27 October 2026

Owner requests required submission fields, optional promotions signup and lead generation section. Acceptance: visible required markers and native/server validation for name/message/request category/email on website and phone for callback; marketing email choice unticked/optional/separate and never required for enquiry; record explicit consent text/version/source/time with email and enquiry reference; no implicit marketing consent from enquiry; public self-service unsubscribe plus staff suppression, no campaign sending. Staff Leads lists deduplicated enquiry contacts, source/interest/status/current email preference and linked enquiry; manual capture uses existing staff enquiry workflow, no staff-created marketing consent. Saved demo mirrors leads/consent without real API writes. Preserve existing records via migration, protect leads from public/customer access, local only.

## Authorized hosted release — 27 October 2026

Owner requests publication of the current local work. Verify migrations against dedicated development then production with backups and preserved-record counts; expand actual PostgreSQL CI coverage to customer accounts, enquiries and leads; trust exact source CI before production promotion; do not expose local verification previews publicly. Customer email-provider decision requested separately. Retain old deployment/backup references and verify hosted access, persistent browser demo and relevant real staff paths. No paid plans or rewritten history.

Hosted release prerequisite: replace process-local public enquiry/unsubscribe budgets with bounded atomic database windows shared across serverless instances, retain an explicit PUBLIC_ENQUIRIES_ENABLED switch, cap public JSON before parsing and hide unavailable hosted registration/recovery rather than exposing local email previews. This prepares safe publication irrespective of the pending email-provider choice.

Release rollback acceptance: run the unchanged previous application image against the additive schema without invoking its obsolete migration graph; preserve the current image normal migration startup for forward recovery. Verify saved records and sessions in both directions and retain failure logs.
