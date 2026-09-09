# Task 04 — brief

Plan: .planning/power/features/sdd-composy-f08-fleet/plan.md
Generated: 2026-09-09T12:33:15Z

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

## Task 04 — Headless and tmux UI adapters
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/ui-headless.sh`, `plugins/sdd-composy/scripts/fleet/ui-tmux.sh`, `plugins/sdd-composy/scripts/fleet/launch.sh`, `tests/test_sdd_composy_fleet.py`
Interfaces:
  Consumes: bound runner vector and selected UI driver
  Produces: detached headless process or isolated tmux session/window without changing core lifecycle truth
Steps:
- [ ] Add failing selection, command quoting, missing-tool fallback, collision, and teardown-handle tests.
- [ ] Run the fleet test and observe failures.
- [ ] Implement headless and tmux adapters plus explicit fallback selection.
- [ ] Re-run the fleet test.
- [ ] Commit only when explicitly authorized.
