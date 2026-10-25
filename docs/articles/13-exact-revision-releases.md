# Releasing the revision that actually passed CI

Mohammed Sheikh-Noor · 25 October 2026

A green check on one commit does not prove that a different deployment was tested. Dealer Desk gates delivery on a successful trusted GitHub Actions run for the exact source revision.

The release check verifies the repository, workflow path, push event, main branch and commit SHA. Development delivery waits for that result. Production follows a separate production-release branch, advanced by an explicit promotion command after the check passes.

Development and production use separate Neon branch endpoints. Connection strings remain server-side, and schema migrations run explicitly outside a web request or hosted build. Public production browsing is accessible while staff data still requires app login.

After the mobile release, public health identified bbf5a3f, the catalogue returned ten listings and anonymous staff API reads returned 401. Compatible rollback and forward recovery have also been rehearsed. Code rollback does not undo database changes, so release recovery and database restoration remain separate concerns.

[Release gate](../../scripts/release_gate.py) · [Promotion command](../../scripts/promote.py) · [Recovery runbook](../release-recovery.md)

[AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp)

#aidevtools #DataTalksClub #BuildInPublic #SoftwareEngineering
