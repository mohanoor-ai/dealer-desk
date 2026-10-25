# Protected development and production

Owner: Mohammed Sheikh-Noor. Personal project; fictional review data only.

| Environment | Vercel project | Git source | Database | Access |
|---|---|---|---|---|
| Development | dealer-desk-dev | main after exact-revision CI guard | Original dedicated Neon branch | Vercel Authentication plus staff login |
| Production copy | dealer-desk-prod | production-release, manually advanced after main CI | Separate dealer-desk-prod Neon branch | Vercel Authentication on All Deployments plus staff login |

Development URL: https://dealer-desk-dev.vercel.app/

Production URL: https://dealer-desk-prod.vercel.app/

Production setup was authorized on 25 October 2026. The Vercel project was created empty, renamed and protected before application code or the database connection was attached. The dedicated connection is a Production-only secret; no Preview or Development secret was added to this project. System environment variables remain enabled so the build gate can check the source SHA. FastAPI and Node 24 are selected. Only production builds are enabled for this project; unrelated branch previews are skipped.

The Neon branch is isolated from later development writes. It was created from the existing synthetic snapshot, including the schema, one test vehicle and existing staff account hashes; copied sessions were revoked on the new branch. The inherited database name is still dealer_desk_dev, but it is reached through the separate production branch endpoint. No connection string is published here.

Both consoles remained on their existing Hobby/Free plans. No paid environment, custom domain purchase, paid build machine, on-demand concurrent build or bypass secret was enabled. The old generated project hostname is retained as a redirect to the free production hostname.

## Release

1. Finish the change on main and wait for its exact-commit CI result.
2. Review the chosen full SHA and run `uv run python -m scripts.promote <sha>`.
3. The production branch push triggers the protected production deployment. The first setup deployment can also be explicitly created from that branch in the dashboard.
4. Inspect the deployment source/gate, then verify protected health and the staff journey. The health endpoint in the next release reports a validated source revision; earlier releases report status and application version only.
5. Use a compatible known-good production deployment for rollback, then repeat smoke checks. Never choose a release affected by an unresolved security advisory.

The security-fixed first production revision is 5fc3aae. Its CI passed before the branch was advanced; the first cloud deployment and later rollback results are recorded in verification.md after observation. Creating a project or starting a build is not proof of a healthy release.
