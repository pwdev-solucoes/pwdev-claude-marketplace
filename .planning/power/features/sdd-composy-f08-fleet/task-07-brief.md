# Task 07 — brief

Plan: .planning/power/features/sdd-composy-f08-fleet/plan.md
Generated: 2026-09-09T12:55:24Z

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

## Task 07 — Teardown and authorized merge
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/teardown.sh`, `plugins/sdd-composy/scripts/fleet/common.sh`, `tests/test_sdd_composy_fleet.py`, `tests/test_sdd_composy_fleet_runner.py`
Interfaces:
  Consumes: exact member identity and optional explicit merge authorization
  Produces: verified service/UI shutdown; preserved worktree without merge or no-ff merged branch with post-merge verification
Steps:
- [ ] Add failing tests for non-terminal merge refusal, no authorization, conflict abort, cleanup failure, foreign resource protection, and recoverable preservation.
- [ ] Run both fleet test modules.
- [ ] Implement bounded teardown and merge guards without deleting unknown data or volumes.
- [ ] Re-run both fleet modules.
- [ ] Commit only when explicitly authorized.
