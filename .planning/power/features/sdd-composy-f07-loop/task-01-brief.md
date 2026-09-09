# Task 01 — brief

Plan: .planning/power/features/sdd-composy-f07-loop/plan.md
Generated: 2026-09-09T11:01:28Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- The default autonomous loop limit is 3 iterations.
- Never let autonomous execution change approved requirements, stories, architecture, or scope.
- Stop on completion, iteration cap, no progress, scope expansion, architectural ambiguity, destructive action, external authorization, unrecoverable environment failure, or cancellation.
- A completion phrase is never proof; fresh `sdd-verify` evidence is required.
- Runtime-specific provider command vectors are built only in dedicated adapters.

## Task 01 — Loop state machine
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_loop.py`, `plugins/sdd-composy/references/loop.md`, `tests/test_sdd_composy_loop.py`
Interfaces:
  Consumes: a ready task ID and maximum iterations from 1 through 3
  Produces: `start`, `status`, `continue`, `cancel`, and validated loop-state transitions
Steps:
- [ ] Add failing tests for every stage, legal transition, terminal reason, invalid cap, and atomic state publication.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_loop` and observe failure.
- [ ] Implement provider-neutral state and CLI operations.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
