# Task 04 — brief

Plan: .planning/power/features/sdd-composy-f04-tasks/plan.md
Generated: 2026-09-09T08:30:19Z

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

## Task 04 — Evidence and completion guards
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_tasks.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: task transition engine and evidence records
  Produces: guarded `qa_required`, `review_required`, `verify_required`, `complete`, and `skipped` transitions
Steps:
- [ ] Add failing tests for stale evidence, missing tests, blocking QA/review, rejected verification, unjustified skip, and valid completion.
- [ ] Run the focused test and observe failures.
- [ ] Implement completion predicates and timestamp validation.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
