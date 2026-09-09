# Task 03 — brief

Plan: .planning/power/features/sdd-composy-f08-fleet/plan.md
Generated: 2026-09-09T12:23:18Z

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

## Task 03 — Runtime engines and runner
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/engine-codex.sh`, `plugins/sdd-composy/scripts/fleet/engine-claude.sh`, `plugins/sdd-composy/scripts/fleet/run.sh`, `tests/test_sdd_composy_fleet_runner.py`
Interfaces:
  Consumes: registered member, task contract, loop/result schemas
  Produces: runtime-fixed stage results, process-group cleanup, commits inside fleet branch, and terminal member status
Steps:
- [ ] Add failing command-vector, dangerous-mode acknowledgement, runtime mismatch, process-group, malformed-result, contract-change, and loop-cap tests.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_fleet_runner` and observe failure.
- [ ] Implement dedicated engines and shared runner with fail-closed validation.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
