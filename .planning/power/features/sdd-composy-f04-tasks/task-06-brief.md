# Task 06 — brief

Plan: .planning/power/features/sdd-composy-f04-tasks/plan.md
Generated: 2026-09-09T08:40:43Z

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

## Task 06 — Divergence inspection and plan
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_sync.py`, `plugins/sdd-composy/references/synchronization.md`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: Markdown task contracts and JSON task state
  Produces: read-only `inspect` and deterministic `plan` with conflict classifications and confirmation token
Steps:
- [ ] Add failing tests for no-change, one-sided addition, changed identity, status divergence, and malformed source.
- [ ] Run the focused test and observe failure.
- [ ] Implement comparison without choosing a conflicting authority.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
