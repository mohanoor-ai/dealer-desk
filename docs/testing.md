# Verification commands

Prepare Python 3.12+, uv and Node 24. From the repository, run `uv sync --frozen` and `npm ci --prefix frontend` once. Run the core suite with:

```sh
uv run python -m scripts.verify
```

This single command runs pytest, frontend tests, the TypeScript/production build and the limited source/history audit. Any failed command stops verification and returns its exit code. It does not deploy or modify the hosted database. Dependency installation needs internet; test databases are temporary local files.

## Layers

- tests/test_auth.py: real SQLite integration for authentication, sessions and roles.
- tests/test_journey.py: real database relationships, restart persistence, validation and competing edits.
- tests/test_photos.py: image decoding/limits, metadata handling and persistence.
- tests/test_contract.py: implemented OpenAPI compared with the committed contract.
- tests/test_hosting.py: hosting configuration, headers and static-asset recovery.
- tests/test_catalogue.py: public response/image boundaries and authenticated staff API separation.
- tests/test_operations.py and tests/test_mcp.py: real local signal collection/correlation, policy and read-only protocol checks.
- Frontend Vitest tests: interface behaviour, enquiry/task lifecycle, direct links, scheduling context, editor markers, mobile menu opening/closing and navigation, and browser-demo isolation; these are not real-browser or live-database tests.

For the optional local PostgreSQL regression, use a disposable database named dealer_test on localhost/127.0.0.1, set TEST_DATABASE_URL privately, then run `uv run python -m pytest tests/test_auth.py tests/test_journey.py tests/test_photos.py`. The fixture creates and removes a random test schema; never point it at business data. CI provisions its own isolated database.

Use `./start.ps1` on Windows or `sh start.sh` on Linux for Docker Compose. The initial manager password is interactive; it is not a shipped credential. See README for prerequisites. Never remove a database volume you need.

## Evidence limits

Actual output and dates are in verification.md and docs/evidence. Existing browser screenshots are manual checks, not automated browser regression. A manual independent-session conflict/polling check and actual saved enquiry workflow have evidence. Automated cross-engine browser coverage and a fresh local interactive Docker setup are not claimed. Hosted CI verifies clean Compose HTTP startup, replacement and compatible rollback/forward recovery. API concurrency tests remain a separate layer.
