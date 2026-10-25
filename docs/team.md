# Responsibilities

Mohammed Sheikh-Noor is the product owner and project author. He chooses scope, supplies account authorizations and credentials directly to the relevant service, reviews user-facing behaviour, and approves final submission. This project is developed with AI assistance.

The coding assistant implements authorised changes, reads the specification and task tracker, checks contracts and security boundaries, runs verification, and records actual results. It must distinguish its observations from owner reports. It cannot invent independent reviews, personal learning reflections or completion evidence.

For this project, specification, implementation, testing and documentation are responsibilities performed within the same assistant workflow. They are not four independently operating agents. No independent specialist review is claimed. A specialist may be delegated a bounded review only when explicitly authorised; record its inputs, findings, disposition and verification if that happens.

The owner retains decisions about publishing personal reflections, new account permissions, paid services, production data and final course submission. See [process](process.md), [AI use](ai-use.md) and [security](security.md).

## Existing execution roles

| Participant or component | Responsibility | Input and output | Boundary |
|---|---|---|---|
| Product owner | Chooses scope, reviews behaviour and authorizes external changes | Reports and decisions recorded in tasks/issues; reviewed changes | Human decisions are not attributed to an agent |
| Coding assistant | Reads modular context and tracker; implements, verifies and documents authorized tasks | Acceptance criteria → code/checks → verification and issue disposition | One assistant workflow, without an invented independent reviewer |
| Stock-read monitor (`ops/watch.py`) | Probes the authenticated stock journey in the isolated rehearsal | Three consecutive failed probes → StockReadUnavailable → direct responder invocation | Automation; not an additional coding or LLM agent |
| On-call policy agent (`ops/responder.py`) | Diagnoses the known local fault and executes the allowlisted recovery, otherwise escalates | Alert invocation → table inspection → fixed repair/escalation; monitor then repeats the failed journey | Fixed marked local database only; no arbitrary commands or hosted writes |

The coding workflow is specification → acceptance → implementation → checks → recorded result, described in [process](process.md) and demonstrated in [issue #5](issue-traceability.md). The runtime workflow is failed stock reads → alert → policy agent → recovery probe and record-preservation check, demonstrated in the [CI incident report](evidence/assessment-ci-incident.json). These are existing roles and actual call paths, not a claim that multiple coding agents independently collaborated. The official team criterion asks for defined responsibilities and a process; it does not explicitly require simultaneous agents or independent review.
