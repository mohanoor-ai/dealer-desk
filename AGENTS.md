# Working instructions

Read product-spec.md and docs/architecture.md before changes. The original Windows installation is reference material and must not be edited.
Keep Python functions small, validate inputs explicitly, and use SQLAlchemy bound parameters. Keep every browser request in frontend/src/api.ts.
Individual accounts use server-side sessions. Enforce roles on the backend. Never put credentials, customer data or the private learning companion in this repository.
Before a task: record acceptance criteria in docs/tasks.md. Then implement, inspect, test, and record the real results in docs/verification.md. Never call a mock a live integration.
Current tests: python -m pytest tests; frontend: npm test and npm run build.

For README images, diagrams and evidence, follow docs/documentation-rules.md. Keep current and planned architecture distinct; never use a simulated demo as proof of live persistence.
