# Architecture decision — first persistent journey

Browser → React/TypeScript → centralized API client → FastAPI → SQLAlchemy → SQLite locally or PostgreSQL in cloud. Alembic controls database schema changes.

React keeps forms and shared views manageable. TypeScript catches mismatched data shapes. FastAPI validates API inputs. SQLAlchemy permits the same small application to use local SQLite and hosted PostgreSQL. Alembic records changes instead of silently recreating tables. Docker Compose will provide the portable full-stack environment; Vercel deployment will use an external database.

These are project decisions, informed by course modules 2–3, not mandatory technologies in the final rubric.

## Security boundary
An operator creates individual users from a local command. Passwords use salted scrypt hashes. Login creates a random session whose hash is stored in the database; the browser receives an HttpOnly SameSite cookie. Sessions expire after eight hours and logout revokes them. Production requires HTTPS and Secure cookies.

Viewer reads; sales reads and changes stock, enquiries and tasks; manager also manages operational exports and audit access. No public self-registration. Demo uses fictional records. All mutations require a custom same-origin request header; no cross-origin API access is enabled.

Each edit uses an atomic SQL update matching ID and revision. A successful change and its audit event commit together. Conflicts return 409. Audit records contain actor ID and action metadata, not customer messages.

## Current boundary
Photo extension decision: store bounded optimized images and thumbnails as database binary fields for portability between SQLite and PostgreSQL and to avoid Vercel filesystem persistence assumptions. Image processing uses Pillow with restricted decoders and explicit limits. At this educational scale (12 images/car, 200 KB optimized output cap each), this is a focused choice; larger businesses should migrate the media repository to object storage. The public demo still needs its overall quota/abuse review before publication.

This milestone proves the persistent journey, authentication and conflict boundary. Public abuse controls, full recovery, cloud setup, comprehensive observability and browser evidence remain separate tasks. Do not deploy this intermediate milestone as a real dealership system.

## Selected hosting — 24 October 2026
Personal deployment target: Vercel for FastAPI and the built React frontend, Neon PostgreSQL for records/sessions, and Cloudflare R2 for photos after its storage adapter/migration is implemented. Current photo persistence remains database-backed. Development is protected until public access controls are verified. See deployment-vercel.md for actual configuration and release blockers. Engineering/course evidence stays in repository docs; private learning content remains outside this application.

## Browser demo boundary — 24 October 2026
Customer/dealer demos run entirely in per-tab JavaScript memory through the central API client. They are explicitly simulated workflows, not authenticated users or shared live database sessions. Business requests are intercepted while demo mode is active, with no network fallback, including after expiry. No guest account, password, cookie or browser storage is created. Samples reset on mode switch/reset and disappear on refresh/close/end; a 30-minute UI timer clears active state. Background browser suspension may delay physical memory clearing until the tab resumes, but operations reject access after expiry. Maximum 50 records per collection and 4,000 characters per write bound memory; photo uploads are unavailable. The backend staff authorization remains the real security boundary. Client role restrictions are UX only and grant no server authority. This avoids public database writes, so does not claim to fulfil the shared-session assessment journey. Public hosting still needs its separate access/abuse review.
