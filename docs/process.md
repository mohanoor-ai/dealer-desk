# Change process

1. Read AGENTS.md, product-spec.md and architecture.md. Check the public [task tracker](https://github.com/mohanoor-ai/dealer-desk/issues) and local tasks.md for scope and acceptance criteria.
2. Record acceptance criteria before editing. Separate implemented behaviour from targets and avoid broad unrelated changes.
3. Implement the smallest complete workflow. Keep browser requests in frontend/src/api.ts and enforce validation and permissions on the server.
4. Inspect the diff and run the relevant checks in testing.md. Fix failures before recording success. For external-service checks, record the actual deployment/commit and avoid credentials in output.
5. Record results, limitations and owner-reported observations in verification.md. Update task status using evidence, then commit and publish authorised changes.

## Actual tracker use

Public issues 1–4 establish deployment, storage, demo and operational acceptance criteria. docs/tasks.md retains detailed slices. The 25 October submission-evidence task was recorded before modular documentation and scripts/verify.py were added. Earlier vehicle/photo and cache-recovery tasks have corresponding verification entries and implementation commits. These are concrete records of the assistant using the tracker; they do not imply every public issue is closed.

## Release boundary

GitHub Actions checks changes; Vercel Git deployment currently operates independently. A green CI run is not a deployment gate. Manual production promotion, tested rollback and full operational recovery remain incomplete. Keep protected development hosting enabled and never describe it as an unrestricted public customer service.
