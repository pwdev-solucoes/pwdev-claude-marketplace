# Task 02 — brief

Plan: .planning/power/features/sdd-composy-f09-language/plan.md
Generated: 2026-09-09T13:33:59Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Never generate artifacts before language is resolved.
- Never translate machine keys, IDs, schemas, filenames, or command names.
- Invalid language values fail without mutation.
- All writes remain atomic and path-confined.

## Task 02 — Init integration
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_init.py`, `plugins/sdd-composy/skills/sdd-init/SKILL.md`, `plugins/sdd-composy/commands/init.md`, `tests/test_sdd_composy_language.py`
Interfaces:
  Consumes: resolver from Task 01.
  Produces: init language prompt/selection shared by Claude and Codex.
Steps:
- [ ] Add failing integration tests for explicit selection, missing prompt, invalid no-write, and persisted reuse.
- [ ] Run the focused language test and observe failure.
- [ ] Integrate init and adapters without duplicating policy.
- [ ] Re-run focused and structural tests.
- [ ] Record report.
