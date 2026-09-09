# Task 05 — brief

Plan: .planning/power/features/sdd-composy-f04-tasks/plan.md
Generated: 2026-09-09T08:36:24Z

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

## Task 05 — Task skill and adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-tasks/SKILL.md`, `plugins/sdd-composy/skills/sdd-tasks/agents/openai.yaml`, `plugins/sdd-composy/commands/tasks.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `sdd_tasks.py import|list|next|start|block|transition|verify`
  Produces: portable `$sdd-tasks` and `/sdd-composy:tasks`
Steps:
- [ ] Add failing route and mutation-boundary tests.
- [ ] Run the structural test.
- [ ] Implement skill, metadata, and thin adapter.
- [ ] Run structural and task tests.
- [ ] Commit only when explicitly authorized.
