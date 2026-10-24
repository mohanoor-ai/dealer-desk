# Release audit — 24 October 2026

Scope: current tracked application source and local Git history. No publication performed. Automated matching can miss secrets; this is evidence of a bounded review, not a guarantee.

Public source should include application code, migrations, dependency locks, tests, deployment configuration, English engineering documentation and licensed sample assets with attribution. Exclude .env files, hosting credentials, databases, backups, private learning material, generated builds, node_modules, local accounts and customer exports. Vercel upload additionally excludes source docs/tests/sample originals because the runtime does not require them.

Known sample photographs have CC BY-SA licence/source/credit metadata in sample-assets/stock/credits.json. Their licences do not license the application code. Runtime uploads and fictional account database remain outside Git. No Git remote is configured in this isolated repository.

Prior milestone reports contain historical course/learning references and test evidence; these are engineering documentation. Product-facing educational labels have been replaced with neutral dealership copy. The private learning companion remains outside this application repository.

Review results and exact automated scan counts will be appended after verification. Before external publication inspect the staged diff and scan the complete reachable Git history. No default account should be created by deployment scripts.

## Recorded result
The limited scanner completed against 90 current source files and two reachable commits: zero remaining findings. Initial PostgreSQL-credential matches in docker-compose.yml across current/history revisions were reviewed as the exact ${POSTGRES_PASSWORD} variable expression; the scanner excludes only that exact expression and still flags literal credentials. No history rewriting was performed. npm audit found a high-severity undici transitive dev dependency issue; after a compatible lockfile update it reported zero vulnerabilities. Release blockers are listed in deployment-vercel.md. This inventory is ready for owner review before publication; it is not a claim that hosted access or customer-data isolation has been verified.
