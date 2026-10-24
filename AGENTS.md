# Working instructions

Read product-spec.md and docs/architecture.md before changes. The original Windows installation is reference material and must not be edited.
Keep Python functions small, validate inputs explicitly, and use SQLAlchemy bound parameters. Keep every browser request in frontend/src/api.ts.
Individual accounts use server-side sessions. Enforce roles on the backend. Never put credentials, customer data or the private learning companion in this repository.
Before a task: record acceptance criteria in docs/tasks.md. Then implement, inspect, test, and record the real results in docs/verification.md. Never call a mock a live integration.
Current tests: python -m pytest tests; frontend: npm test and npm run build.

For README images, diagrams and evidence, follow docs/documentation-rules.md. Keep current and planned architecture distinct; never use a simulated demo as proof of live persistence.

Modular context: docs/team.md defines responsibilities; docs/process.md defines change and release boundaries; docs/testing.md defines verification; docs/security.md defines data/tool permissions and known limits; docs/ai-use.md records actual AI assistance. Run the core suite with `uv run python -m scripts.verify` after dependency setup. Do not claim that one assistant's different responsibilities are independent reviewers.
