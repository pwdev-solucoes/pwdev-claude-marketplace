# Task 06 — brief

Plan: .planning/power/features/sdd-composy-f08-fleet/plan.md
Generated: 2026-09-09T12:45:39Z

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

## Task 06 — Dashboard and status integration
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/dashboard.sh`, `plugins/sdd-composy/scripts/sdd_status.py`, `plugins/sdd-composy/scripts/fleet/ui-cmux.sh`, `tests/test_sdd_composy_fleet.py`
Interfaces:
  Consumes: validated central members and per-worktree status
  Produces: concise one-shot dashboard plus cmux descriptions/colors/flashes and global status snapshot
Steps:
- [ ] Add failing tests for malformed members, truncated messages, safe relative output, status aggregation, and attention transitions.
- [ ] Run fleet and observability tests.
- [ ] Implement dashboard and guarded presentation updates.
- [ ] Re-run fleet and observability tests.
- [ ] Commit only when explicitly authorized.
