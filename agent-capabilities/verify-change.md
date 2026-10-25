# Reusable verification procedure

Read AGENTS.md, the specification and the relevant acceptance criteria. State the exact workflow being changed and the applicable permissions. Inspect code and tests, implement the authorised slice, run `uv run python -m scripts.verify`, then retain actual results and limitations. For an operations change, run the isolated rehearsal and inspect correlated signals before claiming recovery. Never substitute browser-memory demo results for persistent API/database checks.

Report: input revision, changed paths, commands, actual outcomes, unresolved risks, and whether any deployment or database change occurred. Do not claim a review by a different agent unless it happened.
