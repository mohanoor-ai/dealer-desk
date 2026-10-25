# Local extension pack

- Project context: AGENTS.md and modular docs.
- Reusable procedure: agent-capabilities/verify-change.md.
- Specialist definition: custom-agent/operations-reviewer.md; no independent invocation claimed.
- MCP tool: mcp-server/server.py, using the official MCP Python SDK v2.
- Fixed-action guardrail: ops/responder.py and agent-hooks/policy.json.
- Permissions: permissions.md; tests/test_operations.py proves denials and data preservation.

Run `uv run python mcp-server/server.py` through an MCP client using stdio. The only tool is rehearsal_stock_summary, which accepts no inputs and returns synthetic aggregate counts. First run the local rehearsal documented in operations.md. The tool is not installed into the app or connected to a production database.

The response agent in the incident rehearsal is deterministic. It does not call an LLM. A real alert invokes it automatically, it diagnoses the fixed fault, restores the table only when both guard conditions match, and rechecks the same HTTP stock journey. Unrecognized states escalate. Do not represent this as unconstrained AI remediation or a completed independent review.
