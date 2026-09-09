# Task 02 — brief

Plan: .planning/power/features/sdd-composy-f04-tasks/plan.md
Generated: 2026-09-09T08:18:26Z

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

## Task 02 — Task state core
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_tasks.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: F01 tasks schema
  Produces: `import`, `list`, `show`, and schema-verified serialization
Steps:
- [ ] Add failing fixture tests for import, stable IDs, unknown-field preservation, unsafe paths, and atomic writes.
- [ ] Run the focused test and observe failure.
- [ ] Implement parsing, schema-aligned validation, and deterministic output.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
