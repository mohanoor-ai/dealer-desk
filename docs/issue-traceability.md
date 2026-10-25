# Worked task traceability: issue #5

This example records actual assistant execution under the owner's direction. It does not reconstruct a transcript or imply independent PM/engineering/QA agents.

## Report and acceptance criteria

The owner reported two open enquiries but no follow-ups, with no indication of which conversations or next actions needed attention. The owner then requested direct navigation by enquiry number and ordinary customer/dealer wording.

[Public issue #5](https://github.com/mohanoor-ai/dealer-desk/issues/5) captured the problem and proposed acceptance criteria before implementation. The dated task entry in [tasks.md](tasks.md) recorded the selected implementation slice. Recorded requirements: open-enquiry navigation, explicit missing next actions, linked/preselected scheduling, overdue/today/upcoming labels, task completion without implicit enquiry closure, closed-enquiry exclusion and retained viewer restrictions.

## Context and execution

The assistant read AGENTS.md, the specification, architecture and existing Pages/WorkForms/navigation/API code. The owner selected scope and supplied UI feedback. The same assistant implemented and checked the change; no independent specialist was invoked.

| Change | Source record |
|---|---|
| Attention list, direct count/record links, scheduling context and regression tests | [8f23b3e](https://github.com/mohanoor-ai/dealer-desk/commit/8f23b3ee4226ee3a66caa30814575d83f9ad3d5b) |
| Ordinary demonstration wording and customer-facing labels | [0b1aff9](https://github.com/mohanoor-ai/dealer-desk/commit/0b1aff92713137a20f8007f212068c347cb4dd6d) |
| Actual overview/collage, provenance and local output | [ead35cf](https://github.com/mohanoor-ai/dealer-desk/commit/ead35cf1e079f54b18309319222db52b3bb98767) |
| Hide the internal catalogue marker in the editor | [81b7015](https://github.com/mohanoor-ai/dealer-desk/commit/81b70159d83479c71a8e6b732beca9d0258c36f7) |
| Reject blank model names before restoring that marker | [14f075b](https://github.com/mohanoor-ai/dealer-desk/commit/14f075b938b1cc4a3812edaea87c6d12d7b7f6b7) |

Primary files: frontend/src/Pages.tsx, workflow.ts, navigation.ts, WorkForms.tsx, App.tsx and api.ts. Acceptance mapping: product-spec.md E3, U1 and the existing server permission boundary.

## Verification and corrections

The new workflow tests cover the unscheduled → scheduled → completed lifecycle, exact links, closed-enquiry exclusion, delayed preselection, submitted task payload, date classification and viewer controls. The editor regression checks marker preservation, duplicate avoidance and empty-name rejection.

A test selector used an unsupported TypeScript option; it was corrected before the passing build. An earlier project check exposed a temporary-directory restriction; required backend checks used a dedicated workspace directory. These were execution failures/corrections, not passing checks.

The retained [local core output](evidence/enquiry-core-checks.txt) has 38 backend and 13 frontend tests. The subsequent editor regression brings the final suite to 14 frontend tests. [CI run 40215259023](https://github.com/mohanoor-ai/dealer-desk/actions/runs/40215259023) passed that final suite, build/audit, PostgreSQL, Docker/Compose replacement, compatible image rollback/forward recovery and local operations labs.

## Actual browser/database evidence

A temporary sales account used a copied local database. Alex Morgan's viewing enquiry was saved through the staff form. The assistant followed enquiry #2, scheduled its internal availability check, reloaded to verify persistence, inspected the saved vehicle status, completed the task and verified the still-open enquiry returned to unscheduled.

[Four-panel collage](media/enquiry-workflow.png) and [capture provenance](media/README.md) retain the observations. The task was reopened/completed to refresh screenshots after wording changes. No customer message or appointment confirmation was sent. The temporary local identity was signed out, disabled and its sessions revoked.

Known demonstration names/messages were updated at the owner's request with private before-images and audit records. Unused operational test cars were archived, not deleted. This is not an import of real customer data.

## Release and closure

After successful trusted main CI, scripts/promote.py advanced production-release to 14f075b938b1cc4a3812edaea87c6d12d7b7f6b7. Production deployment HufgjLEw5138GrNqAKUjYRocw3kX served health metadata matching that SHA. No-cookie checks returned 200 for the homepage/catalogue (ten cars) and 401 for staff vehicles/enquiries/tasks.

Issue #5 was closed with source, CI, workflow and deployment evidence. Its first released fix was ead35cf; the final issue record includes the later editor checks. Subsequent documentation revisions do not change those historical observations.

## Deferred work

No conversation-history feature, staff assignment, automatic customer reply or messaging integration was implemented by this issue. Those remain separate proposals. The example demonstrates actual tracker use and verification, not a self-awarded assessment score.
