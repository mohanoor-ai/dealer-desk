# Public request budgets: fairness proposal

27 October 2026. Proposal only; no runtime controls changed.

Current implementation: backend/public_access.py atomically shares one fifteen-minute database counter per service. Enquiry capture has a 30-request ceiling; registration 20, customer login 40 and unsubscribe 60. Customer registration/login also share a process-local attempt deque. This bounds aggregate writes but lets one client consume another client's capacity. Existing restart tests demonstrate the global cap, not fairness.

## Proposed identity and limits

Keep a global ceiling. Before expensive password hashing or writes, atomically reserve both a service-global allowance and a smaller identity allowance; rollback both if either is unavailable. Repeated rejected requests from an already exhausted client must not consume additional global reservations. Global exhaustion must still reject all clients.

Use an authenticated customer ID for owned conversation routes. For anonymous login/signup, use a short-lived keyed hash of the client address from the deployment's verified proxy boundary. Never trust arbitrary X-Forwarded-For or a client-supplied account ID. Confirm the actual Vercel/ASGI trusted-proxy contract before implementing; do not assume a header is trustworthy. Do not use a submitted email as the sole identity: it lets attackers target somebody else's allowance and exposes an enumeration channel.

Store fixed-window keys with expiry and a hard row cap. A bounded shared overflow bucket handles new identities when the cap is reached; active entries are not evicted to reset their allowance. Expired entries are cleaned in bounded batches. Store no raw addresses in counters or exported logs. Document key rotation and IPv6 normalization before rollout. A NAT can represent several genuine customers; address limits need conservative thresholds.

Separate sign-in and signup counters; separate account-based post-login limits from anonymous limits. Validate retry behaviour without leaking whether an email has an account. Thresholds require actual usage data; the model's numbers below are illustrative and are not production settings.

## Acceptance examples

The isolated model in tests/test_budget_fairness_proposal.py demonstrates the decision order: client A uses its small allocation, its further failures do not spend the remaining global allowance, and client B can proceed. It also shows global exhaustion still blocks B and a fixed capacity bounds identity storage. This is a model test, not proof that the production limiter implements fairness or handles competing SQL requests.

Before runtime implementation: test real concurrent SQL reservations on SQLite/PostgreSQL, restart/multiple-instance behaviour, verified proxy identity, NAT/IPv6 effects, spoofed headers, overflow saturation and expiry. A distributed attacker can still exhaust the global ceiling; no complete bot protection is claimed. Any deployment requires separate owner authorization.
