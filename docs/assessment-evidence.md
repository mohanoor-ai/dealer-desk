# Assessment criteria and reproduction guide

Reviewed 25 October 2026 against the [official project rubric](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/blob/526d9c12506c159e7a8f3cef30e5de1eeaec287b/project/README.md#criteria), the latest change to that file at review time. There are twelve criteria and 24 available points. The maxima below describe the rubric, not awarded marks. Mohammed Sheikh-Noor is the project author; implementation and checks used AI assistance.

## Criterion map

| Official criterion | Maximum | Implementation and direct evidence | Reproduction or inspection |
|---|---:|---|---|
| Problem Description | 2 | [README problem, functionality and expected behaviour](../README.md#problem-description) | Compare customer browsing and staff workflows with the described scope |
| Product Specification | 2 | [Specification](../product-spec.md), [public task tracker](https://github.com/mohanoor-ai/dealer-desk/issues), [acceptance/task record](tasks.md), [worked issue #5](issue-traceability.md) | Follow the report, acceptance, assistant execution, code/checks and issue disposition |
| Agent Team Specification | 2 | [Existing participants, agent responsibilities and input/output boundaries](team.md), [task and release process](process.md) | Coding assistant works from acceptance through checks; the runtime monitor invokes the on-call policy agent. No independent coding review is claimed |
| Context Management | 2 | [AGENTS.md](../AGENTS.md) links modular specification, architecture, team, process, testing, security and AI-use documents | Read the instructions and follow those links |
| Application | 2 | [Connected frontend/API/database architecture](architecture.md), [saved enquiry workflow](../README.md#workflow-in-practice), [API/database integration tests](../tests/test_journey.py) | Run the single OS setup command below, save vehicle/enquiry/task records, reload and inspect persistence |
| Testing | 2 | [Core verification command](../scripts/verify.py), [unit/API/database tests](testing.md), [38 backend and 16 frontend checks](evidence/assessment-core-checks.txt), [successful CI](https://github.com/mohanoor-ai/dealer-desk/actions/runs/40225569002) | `uv run python -m scripts.verify` runs the required local layers in one command; CI separately adds PostgreSQL and containers |
| Containerization | 2 | [Dockerfile](../Dockerfile), [Compose](../docker-compose.yml), [startup scripts](../README.md#docker-compose), [actual clean-container journey](evidence/assessment-ci-container.txt) | `./start.ps1` on Windows or `sh start.sh` on Linux builds/starts app and PostgreSQL and prompts for the first account |
| Deployment | 2 | [Public production website](https://dealer-desk-prod.vercel.app/), [deployment runbook](deployment-vercel.md), [read-only review result](evidence/assessment-review.json) | Browse publicly; `/health` reports the running source revision; staff API calls without login return 401 |
| CI/CD | 3 | [Workflow](../.github/workflows/ci.yml), [exact-revision gate and manual production promotion](release-recovery.md), [container rollback/forward output](evidence/assessment-ci-rollback.txt), [observed cloud recovery](evidence/cloud-recovery.json) | Inspect successful core/PostgreSQL/Compose/recovery stages and separate dev/main versus production-release delivery. Do not promote merely to review |
| Observability | 2 | [SDK instrumentation](../backend/telemetry.py), [collector/storage/UI](../ops/collector.py), [real correlation test](../tests/test_operations.py), [dashboard and scope](operations.md) | Run the isolated collector/rehearsal below; a request span, log and metric exemplar share a trace ID. Only bounded metadata is exported |
| Alerting on User Impact | 1 | [Authenticated stock-read monitor](../ops/watch.py), [CI incident report](evidence/assessment-ci-incident.json) | Three failed reads of the actual user journey create StockReadUnavailable |
| On-Call Agent | 2 | [Bounded responder](../ops/responder.py), [automatic invocation](../ops/watch.py), [observed repair and recovery](evidence/assessment-ci-incident.json), [call-path explanation](operations.md#automatic-recovery-path) | Alert automatically invokes diagnosis and fixed repair; the same HTTP read recovers and the saved vehicle remains |

## Reviewer commands

Prerequisites and account setup are in the [README](../README.md#run-locally). Use a fresh checkout and fictional review records, never real customer data.

```sh
# Windows PowerShell: ./start.ps1
# Linux:
sh start.sh
```

The startup command includes first-manager creation through an interactive prompt; no shared password is shipped. The private staff journey is separate from the optional browser-memory demonstration. Completing a demo is not evidence of database persistence.

After installing Python/Node dependencies as documented:

```sh
uv run python -m scripts.verify
```

This includes unit, API/database integration and frontend interaction tests, build and the limited source audit. CI adds 18 PostgreSQL integration checks, clean Compose HTTP creation, app replacement, previous-image rollback, forward restoration and the operations rehearsal. See [CI run 40225569002](https://github.com/mohanoor-ai/dealer-desk/actions/runs/40225569002) and its implemented-api artifact.

For observability/alert/repair, use a fresh checkout with no existing rehearsal database. In one terminal:

```sh
uv run python -m ops.collector
```

In a second terminal:

```sh
uv run python -m ops.rehearse
uv run python -m ops.backup_lab
```

Open http://127.0.0.1:8790/ to inspect stored correlation. The script refuses to overwrite an existing rehearsal database. Do not delete a database to rerun it; use another fresh checkout. The fault and recovery are restricted to the marked loopback SQLite lab, with no production fault injection.

## On-call and team interpretation

The on-call criterion specifies automatic alert response and issue repair; it does not require an LLM, a particular vendor, production fault injection or general-purpose reasoning. In the retained CI run, `monitor` calls `respond` after the third failure, the policy agent diagnoses the known table state and restores it, and the monitor verifies HTTP recovery. The rehearsal additionally checks record preservation. No human repair step intervenes. This is a direct match for the published behaviour, with a deliberately narrow permission boundary.

The team criterion concerns defined roles and their process. [The team specification](team.md) names the actual owner, coding assistant, monitor automation and runtime policy agent, and records their responsibilities and interactions. One coding assistant performing implementation and checking is not an independent multi-agent review. No such review is needed to claim the documented process, and none is invented here. Reviewers retain the final scoring decision.

## Verification checkpoint and provenance

The incident/container/rollback/backup files linked above were copied without content changes from artifact 12610588755 of successful CI 40225569002 at clean source `389bd146394bb740e33e26657629561215599c22`. [Artifact provenance](evidence/assessment-review.json) records its verified SHA-256. The incident report contains source revision, three 503 trace IDs, repair decision, 200 recovery and record preservation. Historical local reports remain separately dated.

A read-only production check during this review found healthy revision `bbf5a3fbc7ace63f82fe5e4e792fb5221d9a2609`, ten public catalogue listings and anonymous staff stock access denied. Source `389bd14` changes only documentation/media from that runtime release. This review does not promote a production release or alter hosted settings/data. Final review-commit CI is available through Actions; observations are recorded in [verification](verification.md).

## Limits and submission

No confirmed missing implementation was found against the published criteria. Final marks remain a peer-review decision. Local Docker Desktop was unavailable during prior local checks; hosted CI provides the actual clean Compose and recovery results. Managed production telemetry, Grafana/LGTM, LLM diagnosis, independent coding-agent review and automated cross-engine browser coverage are not claimed and are not explicit requirements of this rubric.

The course form already saved source `389bd14` on 25 October at 19:28 Europe/London. This documentation review creates a later repository revision; it does not silently change the saved submission or production. Three assigned peer reviews remain compulsory. Optional article work is separate from the twelve scored criteria and is not a reason to add unrelated features to this review.
