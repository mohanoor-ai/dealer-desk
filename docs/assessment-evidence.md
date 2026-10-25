# Assessment evidence index

Prepared 25 October 2026 for Mohammed Sheikh-Noor. This is an evidence index, not a self-awarded grade or a completion certificate.

Official requirements checked against course revision [de41e409](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/blob/de41e4096d8ac08db3852dfda4ce802f9ac0c0d2/project/README.md). The current document defines 12 criteria, 24 available points, a 10-point pass threshold and three compulsory peer reviews. The submission form requests a public repository and exact commit; it does not request hosted account credentials. Deployment evidence remains a separate rubric criterion.

| Criterion | Evidence in this repository | Limitations |
|---|---|---|
| Problem description | README; project-overview.md | One dealership, fictional review data |
| Product specification | product-spec.md; tasks.md; public issues 1–4; process.md tracker-use examples | Targets and incomplete work remain explicitly labelled |
| Agent team specification | team.md; process.md | Responsibilities are defined; no independent specialist or fictitious handoff claimed |
| Context management | AGENTS.md links modular architecture, team, process, testing, security and AI-use docs | Instructions do not prove all features completed |
| Application | Connected staff interface/API/database; verification.md; screenshot and capture provenance | Final clean interactive setup and repeatable two-browser check still need evidence |
| Testing | `uv run python -m scripts.verify`; tests/ and frontend tests; evidence/submission-core-checks.txt | Core command covers local SQLite and frontend; PostgreSQL and real browsers are separate |
| Containerization | Dockerfile; docker-compose.yml; start.ps1; start.sh; earlier replacement/persistence evidence | Docker engine did not complete a fresh check on 25 October |
| Deployment | deployment-vercel.md; hosted journey/redeployment evidence; media/dealer-overview.png with source commit | Protected Vercel development deployment; no unrestricted showroom claimed |
| CI/CD | .github/workflows/ci.yml; hosted workflow history; Vercel Git deployment evidence | Independent CI and deploy; no passing-test gate, production promotion or rollback rehearsal yet |
| Observability | backend/telemetry.py; ops/collector.py; operations.md; real correlation screenshot | Local OTLP collector, SQLite storage and correlation UI demonstrated; no production telemetry service claimed |
| Alerting | Three failed authenticated stock reads triggered StockReadUnavailable; incident-rehearsal.json | Isolated local rehearsal, not a production alert service |
| On-call agent | Alert automatically invokes ops/responder.py; 503 to 200 and record preservation recorded | Deterministic policy agent; no LLM diagnosis or autonomous production repair claimed |

The agent extension pack is separate module scope, not a thirteenth scoring row in this pinned final rubric. See agent-extension-pack.md for the runnable read-only MCP tool, reusable workflow, specialist definition and enforced guardrail. No independent specialist invocation is claimed. Security/data boundaries and the limited source/history scanner are documented in security.md. Optional articles are indexed in articles/README.md; drafts are not published progress links.

## Reviewer route

1. Read the README and run the local setup command for your OS after installing Docker.
2. Create the initial manager account through the interactive prompt; there is no shared shipped password.
3. Use fictional records to add a vehicle, enquiry and follow-up, complete it, and reload to inspect persistence and totals.
4. Run the verification command and inspect the test layers and retained output.
5. Read verification.md for observations tied to actual commits, environments and known limits.

Do not send real customer records or secrets to the assistant, article drafts or course submission. The final evaluated revision is supplied in the course form after the last checks; it is not embedded here because that would change the revision itself.
