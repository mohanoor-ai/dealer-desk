# Task tracker

This file is intended to be public with the reviewed application source. Hosted tracker publication is pending.

| ID | Acceptance criteria | State |
|---|---|---|
| DEP01 | Vercel entrypoint and frontend build; no migrations at import/build; hosted startup rejects SQLite/missing TLS, secure cookies and bounded connections | Prepared; local tests/build pass, hosted verification pending |
| DEP02 | Tracked-source/history release audit, exclusion rules and deployment runbook; report blockers without claiming publication | Local audit complete; owner publication review pending |
| J01 | Operator creates individual user; valid login works; invalid login and viewer writes fail; logout revokes session | Verified by API tests; full interactive bootstrap still pending |
| J02 | Vehicle → enquiry → follow-up persists after app restart; completion updates dashboard | Verified on SQLite and PostgreSQL; browser reload verified |
| J03 | Stale edit returns 409 and does not overwrite; audit contains actor, ID and revision | Verified, including two simultaneous API edits |
| J04 | UI uses real API; usable loading/error/empty states; no product screen course jargon | Browser journey and basic responsive check passed; full accessibility review pending |
| J05 | Schema migrates on SQLite and PostgreSQL; clean Compose start and restart preserves data | Startup migrations, readiness and application-container replacement passed; clean interactive setup pending |
| J06 | Browser journey, roles, recovery and hosted CI/CD evidence | Planned |
| J07 | Current rubric operations/alert/responder evidence; safe extensions | Planned |
| J08 | Release archive, offline companion, public/private inventory and final submission | Planned |
| UX01 | Separate overview, stock, enquiries, follow-ups and linkable vehicle-detail pages; browser Back works | Implemented; see verification.md for passed checks and pending browser/PostgreSQL checks |
| UX02 | Licensed stock illustrations with visible credits; no illustration represented as the actual stock vehicle | Implemented; see verification.md for passed checks and pending browser/PostgreSQL checks |
| UX03 | Staff can upload multiple JPEG/PNG/WebP photos, browse a gallery and choose a cover; viewers cannot upload | Implemented; see verification.md for passed checks and pending browser/PostgreSQL checks |
| UX04 | Photos survive restart on SQLite/PostgreSQL; size/type/dimension limits, EXIF stripping and conflict checks verified | Implemented; see verification.md for passed checks and pending browser/PostgreSQL checks |
