# System and workflow diagrams

Documentation checkpoint: 25 October 2026. Staff architecture remains the b01d342 baseline; release and operations diagrams include the verified release/recovery work; application interface/navigation evidence extends through 14f075b. Mermaid source is editable in this file and the README; no external diagram service is required to edit it.

## Current: hosted application

```mermaid
flowchart TB
    Public[Production visitor] --> UI[React frontend on Vercel]
    Dev[Development visitor] --> Gate[Vercel Authentication on development]
    Gate --> UI
    UI --> Catalogue[Read-only reference catalogue API]
    UI --> Staff[Staff session and role checks]
    Staff --> API[Stock, enquiries and follow-ups]
    Catalogue --> DB[(Separate Neon branch per environment)]
    API --> DB
    DB --- Photos[Processed image bytes and credits]
    DB --- Records[Vehicles, enquiries, tasks and audit records]
```

Production browsing is public; customer records and mutations require staff app authentication. Development and previews retain Vercel protection. Catalogue responses exclude private records. Temporary browser demos are memory-only simulations outside this persisted path. R2 and Grafana/LGTM are not deployed. See architecture.md and environments.md for boundaries.

## Current: staff save and conflicting edits

```mermaid
sequenceDiagram
    actor Staff
    participant UI as React client
    participant API as FastAPI
    participant DB as Database
    Staff->>UI: Edit saved vehicle
    UI->>API: PATCH fields and opened revision
    API->>API: Validate session, role and fields
    API->>DB: Atomic update matching ID and revision
    alt Revision matches
        DB-->>API: One row updated
        API->>DB: Commit update and audit event
        API-->>UI: Saved record with new revision
        UI->>API: Refresh records
    else Another edit already changed the record
        DB-->>API: No matching update
        API-->>UI: 409 conflict; refresh and review
    end
```

The API tests cover permissions and competing edits. A manual independent-session conflict and polling check passed; see verification.md. This is not an automated cross-engine browser suite.

## Current: gated development and manual production

```mermaid
flowchart TB
    Commit[Push reviewed revision to main] --> CI[GitHub Actions: tests, build and recovery labs]
    Commit --> Gate[Vercel build waits for trusted exact-revision CI]
    CI --> Gate
    Gate -->|Success only| Dev[Protected development deployment]
    Dev --> Smoke[Review smoke evidence]
    Smoke --> Manual[Operator runs promote with full revision]
    Manual --> Branch[Advance production-release without force]
    Branch --> Prod[Protected production build checks same CI]
    Prod --> DB[Isolated production Neon branch]
    Prod --> Health[Verify health revision and saved journey]
    Health --> Rehearsal[Compatible release rollback and forward restoration]
```

The cloud rollback/forward rehearsal between security-fixed 5fc3aae and 30dad17 passed. Vercel builds source; the separately tested Docker images are used for local/CI Compose. Code rollback does not undo database writes or schema migrations. An isolated SQLite restore lab is separate from a hosted Neon restore.

## Current local lab: bounded incident response

```mermaid
flowchart TB
    Fault[Rename table in marked synthetic SQLite fixture] --> Request[Authenticated stock requests return 503]
    Request --> Signals[OTLP metrics, logs and traces collected locally]
    Request --> Alert[Three failures trigger stock alert]
    Alert --> Agent[Deterministic policy responder]
    Agent --> Policy{Fixed local path and known fault?}
    Policy -->|No| Escalate[Escalate without mutation]
    Policy -->|Yes| Repair[Restore only the known table name]
    Repair --> Recovery[Same stock journey returns 200]
    Recovery --> Record[Verify record preservation and save report]
```

The responder has no hosted credentials, model-generated commands or arbitrary shell tool. Correlation UI, actual alert and repair are demonstrated in operations.md. Production telemetry and model-backed diagnosis are not claimed.

## Screenshot policy

Use real application/browser captures. State capture date, source commit, environment and whether data is fictional. Preserve error/empty states honestly rather than editing figures. Do not capture credentials, connection strings, personal customer data or account permission dialogs. Put CI, telemetry and incident screenshots with their relevant evidence once those checks exist.
