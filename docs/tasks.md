# Task tracker

This file is intended to be public with the reviewed application source. Hosted tracker publication is pending.

| ID | Acceptance criteria | State |
|---|---|---|
| J01 | Operator creates individual user; valid login works; invalid login and viewer writes fail; logout revokes session | Verified by API tests; full interactive bootstrap still pending |
| J02 | Vehicle → enquiry → follow-up persists after app restart; completion updates dashboard | Verified on SQLite and PostgreSQL; browser reload verified |
| J03 | Stale edit returns 409 and does not overwrite; audit contains actor, ID and revision | Verified, including two simultaneous API edits |
| J04 | UI uses real API; usable loading/error/empty states; no product screen course jargon | Browser journey and basic responsive check passed; full accessibility review pending |
| J05 | Schema migrates on SQLite and PostgreSQL; clean Compose start and restart preserves data | Startup migrations, readiness and application-container replacement passed; clean interactive setup pending |
| J06 | Browser journey, roles, recovery and hosted CI/CD evidence | Planned |
| J07 | Current rubric operations/alert/responder evidence; safe extensions | Planned |
| J08 | Release archive, offline companion, public/private inventory and final submission | Planned |
