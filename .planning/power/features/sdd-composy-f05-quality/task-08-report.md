---
type: TASK_REPORT
okf_version: "0.2"
status: APPROVED
generated_by: /root/f05_task08
verified_by: /root/f05_task08
source: task-08-brief.md
---

# Task 08 — Evidence skill and adapters

## Result

Implemented the portable `sdd-evidence` skill, OpenAI runtime metadata, and the thin
Claude `/sdd-composy:evidence` adapter. The skill documents discovery of existing evidence,
manifest rebuild/verification, confined relative paths and SHA-256 digests, optional HTML
and PDF routing, and the existing task-engine guard for `evidence_required` →
`review_required`. No lifecycle guard was weakened.

Round 1 correction added operational CLI routes for `discover`, `build`, `verify`, and
`export` (including guarded optional PDF behavior), deterministic read-only discovery, and
RFC3339 UTC `generated_at` manifest metadata validated against the published schema.

## Verification

Command: `python3 -m unittest tests.test_sdd_composy_quality tests.test_sdd_composy_tasks`

Result: `Ran 70 tests ... OK`.

The new tests cover adapter discovery/routing, existing-evidence rebuild without source
mutation, CLI routing, optional-PDF documentation, and rejection of a guarded lifecycle transition when
the evidence dossier is absent.

No commit was created.
