# Giving a coding assistant a useful specification

Mohammed Sheikh-Noor · 25 October 2026

Dealer Desk started with a small operational problem: staff need vehicle availability, linked enquiries and the next action in one place. The useful instruction is a behaviour someone can check. For example, completing a follow-up must leave the enquiry open unless staff changes its status.

The repository separates the product specification from architecture, tasks and verification. AGENTS.md points to those files and requires acceptance criteria before implementation. This gives the coding assistant durable context instead of relying only on the latest chat message.

A change to the overview followed that process. The task described direct enquiry-number links, missing next actions and scheduling context. Implementation and checks were recorded against those behaviours. The public issue trace links the report to code, tests and release.

This project used one coding-assistant workflow for implementation and verification. Role descriptions in documents do not establish an independent review. Keeping that limitation explicit makes the record more useful than claiming that several roles automatically mean several reviewers.

[Product specification](../../product-spec.md) · [Project instructions](../../AGENTS.md) · [Issue trace](../issue-traceability.md)

[AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp)

#aidevtools #DataTalksClub #BuildInPublic #SoftwareEngineering
