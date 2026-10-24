# Task tracker

Public tracker: https://github.com/mohanoor-ai/dealer-desk/issues. Issues 1–4 contain the current deployment, R2, showroom/demo and operational acceptance criteria. This table records the detailed local history; docs/verification.md records actual evidence.

| ID | Acceptance criteria | State |
|---|---|---|
| DEP01 | Vercel entrypoint and frontend build; no migrations at import/build; hosted startup rejects SQLite/missing TLS, secure cookies and bounded connections | Local checks and protected Vercel/Neon hosted journey verified; production release remains pending |
| DEP02 | Tracked-source/history release audit, exclusion rules and deployment runbook; report blockers without claiming publication | Reviewed source published to new repository; private runtime files excluded |
| J01 | Operator creates individual user; valid login works; invalid login and viewer writes fail; logout revokes session | API and temporary hosted sales login verified; owner reports manager password created, hosted manager login confirmation pending |
| J02 | Vehicle → enquiry → follow-up persists after app restart; completion updates dashboard | Verified on SQLite and PostgreSQL; browser reload verified |
| J03 | Stale edit returns 409 and does not overwrite; audit contains actor, ID and revision | Verified, including two simultaneous API edits |
| J04 | UI uses real API; usable loading/error/empty states; no product screen course jargon | Browser journey and basic responsive check passed; full accessibility review pending |
| J05 | Schema migrates on SQLite and PostgreSQL; clean Compose start and restart preserves data | Startup migrations, readiness and application-container replacement passed; clean interactive setup pending |
| J06 | Browser journey, roles, recovery and hosted CI/CD evidence | Hosted journey and CI verified; CI-gated CD, rollback and recovery pending |
| J07 | Current rubric operations/alert/responder evidence; safe extensions | Planned |
| J08 | Release archive, offline companion, public/private inventory and final submission | Planned |
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
