# Extension and responder permissions

The MCP server uses stdio, accepts no tool parameters and reads only aggregate stock counts from data/rehearsal.sqlite3 using SQLite read-only mode. It cannot choose a database, run supplied SQL, expose customer fields, mutate records or connect to Neon. Starting it does not install it into an external assistant automatically.

The local response agent has one permitted write: rename vehicles_v2_rehearsal_offline back to vehicles_v2 in the fixed synthetic rehearsal database. It requires an explicit marker and refuses hosted environments, other files and other actions. The fixed SQL is reviewed source, never generated from an alert or model output. Authorization is enforced in Python, not merely described by a prompt.

The specialist definition is source-read-only and has no production capability. No external specialist invocation is claimed. Any future model-backed diagnosis must use the same evidence/permission boundary, with no arbitrary commands or production credentials.

Telemetry is opt-in through DEALER_OTLP_ENDPOINT and only permits loopback or the named local telemetry container. Exported fields are bounded route templates, method, status, duration and source/environment metadata. Body, headers, cookies, query strings, record identifiers, customer messages and exception text are excluded. The collector retains at most 1,000 export batches on local disk; it is a development collector, not a production service.
