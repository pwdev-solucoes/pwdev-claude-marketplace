# Task 03 — brief

Plan: .planning/power/features/sdd-composy-f04-tasks/plan.md
Generated: 2026-09-09T08:25:26Z

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

## Task 03 — Dependency and transition engine
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_tasks.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: imported feature-task state from Task 02
  Produces: `next`, `start`, `block`, and `transition` with legal-state enforcement
Steps:
- [ ] Add failing tests for cycles, missing dependencies, ready selection, illegal transitions, blocked reasons, and rejected-to-ready recovery.
- [ ] Run the focused test and observe expected failures.
- [ ] Implement graph validation and exact transition guards.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
