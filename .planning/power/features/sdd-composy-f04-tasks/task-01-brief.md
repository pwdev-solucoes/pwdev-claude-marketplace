# Task 01 — brief

Plan: .planning/power/features/sdd-composy-f04-tasks/plan.md
Generated: 2026-09-09T08:14:08Z

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

## Task 01 — Human task contracts
Complexity: medium
Files: `plugins/sdd-composy/templates/tasks.md`, `plugins/sdd-composy/templates/task.md`, `plugins/sdd-composy/references/tasks.md`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: approved PRD, stories resolution, and TechSpec
  Produces: dependency-explicit task index and per-task contracts
Steps:
- [ ] Add failing tests for IDs, dependencies, RF/US/SC/CA/test links, allowed files, subtasks, and verification commands.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_tasks` and observe failure.
- [ ] Implement the two templates and task contract reference.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
