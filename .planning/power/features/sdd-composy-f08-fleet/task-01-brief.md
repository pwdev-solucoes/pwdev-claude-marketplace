# Task 01 — brief

Plan: .planning/power/features/sdd-composy-f08-fleet/plan.md
Generated: 2026-09-09T12:02:18Z

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

## Task 01 — Fleet core and worktree binding
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/common.sh`, `plugins/sdd-composy/scripts/fleet/launch.sh`, `plugins/sdd-composy/references/fleet.md`, `tests/test_sdd_composy_fleet.py`
Interfaces:
  Consumes: approved ready task, named base branch, clean contract identity
  Produces: locked member record, isolated `sdd-fleet/<id>` branch, sibling worktree, and bound hashes
Steps:
- [ ] Add failing tests for eligibility, symlinks, collisions, dirty contracts, hash binding, partial launch, and central-worktree preservation.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_fleet` and observe failure.
- [ ] Implement safe path validation, lock ownership, branch/worktree setup, and member publication.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
