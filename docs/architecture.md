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
