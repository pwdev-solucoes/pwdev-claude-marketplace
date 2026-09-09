# Task 07 — brief

Plan: .planning/power/features/sdd-composy-f04-tasks/plan.md
Generated: 2026-09-09T08:48:05Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Task IDs are stable and never renumbered after approval.
- A task cannot become `ready` until all dependencies are `complete`.
- A task cannot become `complete` without fresh tests, QA, review, verify, and trace consistency.
- Conflicting Markdown and JSON are never overwritten silently.
- All writes use same-directory temporary files and atomic replacement.
- Preserve unknown JSON fields during supported updates.
- Generated task Markdown is OKF v0.2 and links upstream concepts through `sources` and body links.

## Task 07 — Explicit synchronization apply
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_sync.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: exact synchronization plan token from Task 06
  Produces: atomic `apply` of an explicitly selected resolution
Steps:
- [ ] Add failing tests for stale token, changed inputs, symlink destinations, explicit Markdown choice, explicit JSON choice, and post-apply verification.
- [ ] Run the focused test and observe failures.
- [ ] Implement guarded application and revalidation.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
