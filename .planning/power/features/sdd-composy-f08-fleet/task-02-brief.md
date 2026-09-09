# Task 02 — brief

Plan: .planning/power/features/sdd-composy-f08-fleet/plan.md
Generated: 2026-09-09T12:10:30Z

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

## Task 02 — Ports and isolated services
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/common.sh`, `plugins/sdd-composy/scripts/fleet/launch.sh`, `plugins/sdd-composy/templates/docker-compose.sdd-fleet.yml`, `tests/test_sdd_composy_fleet.py`
Interfaces:
  Consumes: locked fleet capacity and validated configuration
  Produces: deterministic free port slot and isolated Compose project
Steps:
- [ ] Add failing tests for allocation races, invalid ranges, occupied ports, existing runtime files, Compose absence, and rollback bookkeeping.
- [ ] Run the focused test and observe failures.
- [ ] Implement locked allocation, generated mode-restricted environment, and isolated Compose startup.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
