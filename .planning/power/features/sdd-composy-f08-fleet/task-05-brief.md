# Task 05 — brief

Plan: .planning/power/features/sdd-composy-f08-fleet/plan.md
Generated: 2026-09-09T12:39:03Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Fleet accepts only ready tasks with complete dependencies, explicit acceptance criteria, known verification commands, and no confirmed path overlap.
- Never merge fleet branches automatically.
- Preserve recoverable branches and worktrees after failure.
- Runtime-specific provider command vectors are built only in their dedicated adapters.
- cmux is a presentation adapter and must not own process lifecycle truth.
- cmux operations are restricted to the workspace created by this fleet.
- Never read or adopt an existing `.env.fleet`.

## Task 05 — cmux UI adapter
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/ui-cmux.sh`, `plugins/sdd-composy/references/cmux.md`, `plugins/sdd-composy/scripts/fleet/launch.sh`, `tests/test_sdd_composy_fleet.py`
Interfaces:
  Consumes: cmux identify/list/new-workspace/new-split/surface operations and bound member
  Produces: plugin-owned workspace/pane/surface handles, status decoration, and attention flash
Steps:
- [ ] Add failing mocked-CLI tests for unavailable cmux, workspace ownership, handle parsing, no foreign mutation, flash, stale handles, and fallback.
- [ ] Run the fleet test and observe failures.
- [ ] Implement deterministic cmux operations restricted to the recorded workspace.
- [ ] Re-run the fleet test.
- [ ] Commit only when explicitly authorized.
