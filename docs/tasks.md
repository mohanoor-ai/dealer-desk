# Task tracker

Public tracker: https://github.com/mohanoor-ai/dealer-desk/issues. Issues 1–4 contain the current deployment, R2, showroom/demo and operational acceptance criteria. This table records the detailed local history; docs/verification.md records actual evidence.

| ID | Acceptance criteria | State |
|---|---|---|
| DEP01 | Vercel entrypoint and frontend build; no migrations at import/build; hosted startup rejects SQLite/missing TLS, secure cookies and bounded connections | Local checks and protected Vercel/Neon hosted journey verified; separate protected production release and cloud recovery verified |
| DEP02 | Tracked-source/history release audit, exclusion rules and deployment runbook; report blockers without claiming publication | Reviewed source published to new repository; private runtime files excluded |
| J01 | Operator creates individual user; valid login works; invalid login and viewer writes fail; logout revokes session | API and temporary hosted sales login verified; owner confirmed manager login works; later Overview capture used the staff session |
| J02 | Vehicle → enquiry → follow-up persists after app restart; completion updates dashboard | Verified on SQLite and PostgreSQL; browser reload verified |
| J03 | Stale edit returns 409 and does not overwrite; audit contains actor, ID and revision | Verified, including two simultaneous API edits |
| J04 | UI uses real API; usable loading/error/empty states; no product screen course jargon | Browser journey and basic responsive check passed; full accessibility review pending |
| J05 | Schema migrates on SQLite and PostgreSQL; clean Compose start and restart preserves data | Startup migrations, readiness and application-container replacement passed; clean interactive setup pending |
| J06 | Browser journey, roles, recovery and hosted CI/CD evidence | Hosted journey and CI verified; CI-gated CD, container recovery and protected cloud rollback/forward restoration verified |
| J07 | Current rubric operations/alert/responder evidence; safe extensions | Local OTLP collection/correlation, actual alert, bounded deterministic repair, backup lab and read-only MCP verified |
| J08 | Release archive, offline companion, public/private inventory and final submission | Source/companion packaging and final revision bundle prepared separately; owner submission and three peer reviews remain |
| UX01 | Separate overview, stock, enquiries, follow-ups and linkable vehicle-detail pages; browser Back works | Implemented; see verification.md for passed checks and pending browser/PostgreSQL checks |
| UX02 | Licensed stock illustrations with visible credits; no illustration represented as the actual stock vehicle | Implemented; see verification.md for passed checks and pending browser/PostgreSQL checks |
| UX03 | Staff can upload multiple JPEG/PNG/WebP photos, browse a gallery and choose a cover; viewers cannot upload | Implemented; see verification.md for passed checks and pending browser/PostgreSQL checks |
| UX04 | Photos survive restart on SQLite/PostgreSQL; size/type/dimension limits, EXIF stripping and conflict checks verified | Implemented; see verification.md for passed checks and pending browser/PostgreSQL checks |

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
