# Security and operations review — 25 October 2026

Review scope: release guard, opt-in OpenTelemetry, local collector, synthetic recovery, read-only MCP and pinned runtime dependencies. Performed within the implementation assistant workflow; no independent specialist or penetration test is claimed.

## Findings and dispositions

| Finding | Evidence | Disposition |
|---|---|---|
| Vulnerable Certifi trust bundle | PyPA pip-audit reported PYSEC-2026-4320 / GHSA-6q48-6c7w-9gw2 for 2026.7.22 | Upgraded to 2026.10.23 in uv.lock and exported requirements; repeat audit reports no known vulnerabilities |
| Rehearsal initially targeted an unversioned table name | Real first run failed before injection | Corrected to vehicles_v2; preserved failed fixture privately; actual repeat recovered from 503 to 200 |
| Rehearsal resource version initially identified its base commit despite uncommitted changes | Initial local OTLP screenshot/data | Explicit provenance limitation recorded; later report records source commit and dirty state; CI reruns from its checkout |
| Potential unrestricted response actions | Permission tests attempt another path, arbitrary action, hosted environment and missing marker | Denied; one fixed repair and fixed rehearsal path remain the only write capability; symlink checks added |
| Potential private request data in telemetry | Instrumentation and real collector test | Export route templates/method/status/duration only; no bodies, cookies, query strings, customer messages or exception text |
| MCP scope could otherwise expose production data | Actual stdio protocol test | Fixed synthetic file, read-only SQLite, aggregate counts, no parameters; unknown write tool rejected |
| CI and deployment originally ran independently | Earlier verification record | Hosted exact-commit build guard now confirmed in Vercel logs before frontend build |

## Retained scan artifacts

- dependency-audit-before.json: actual known-vulnerability finding.
- dependency-audit.json: actual post-upgrade PyPA report.
- ../docs/evidence/operations-source-audit.txt: limited current-source/reachable-history scan.
- ../docs/evidence/operations-core-checks.txt: core tests/build/scan output.

Command: `uvx pip-audit -r requirements.txt --no-deps --disable-pip --format json --output security/dependency-audit.json`. This scans the explicitly pinned runtime set rather than resolving/installing another environment. It is not a claim that unknown vulnerabilities, development-tool dependencies or deployment configuration are fully audited. See [the advisory](https://github.com/advisories/GHSA-6q48-6c7w-9gw2) for the affected/fixed versions.

## Remaining boundaries

Hosted login protection must stay enabled. The limiter is process-local; unrestricted public writes still need shared limits and quotas. The local collector and deterministic responder are development demonstrations, not a managed production monitoring or LLM on-call service. Production migration compatibility and database restoration require separate operator judgment. The specialist role is defined but has not been independently invoked.
