# Observing a failure before attempting a repair

Mohammed Sheikh-Noor · 25 October 2026

A request returning an error is the start of an investigation, not permission for an agent to run arbitrary commands. Dealer Desk has a controlled local operations rehearsal with a narrow failure and recovery boundary.

OpenTelemetry exports request metrics, structured logs and traces to a loopback collector. Its correlation view joins signals using request trace information. Customer messages, credentials, cookies and request bodies are excluded from these exports.

Three authenticated stock-read failures triggered an alert during the rehearsal. A deterministic responder could inspect and restore only a known renamed table in a fixed, explicitly marked local database. The same read then returned 200 and the saved vehicle remained present.

This was not a hosted production incident, an LLM diagnosis or unrestricted autonomous repair. Grafana, Loki, Tempo and Prometheus are not deployed in this project. The implemented collector and bounded policy demonstrate a smaller scope, and the operations document states that limit.

![Actual local signal correlation](../evidence/operations-correlation.png)

[Operations details and capture provenance](../operations.md) · [Policy and tests](../../tests/test_operations.py)

[AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp)

#aidevtools #DataTalksClub #BuildInPublic #SoftwareEngineering
