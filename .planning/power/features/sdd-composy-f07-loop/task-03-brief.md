# Task 03 — brief

Plan: .planning/power/features/sdd-composy-f07-loop/plan.md
Generated: 2026-09-09T11:11:15Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- The default autonomous loop limit is 3 iterations.
- Never let autonomous execution change approved requirements, stories, architecture, or scope.
- Stop on completion, iteration cap, no progress, scope expansion, architectural ambiguity, destructive action, external authorization, unrecoverable environment failure, or cancellation.
- A completion phrase is never proof; fresh `sdd-verify` evidence is required.
- Runtime-specific provider command vectors are built only in dedicated adapters.

## Task 03 — Progress and correction limits
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_loop.py`, `tests/test_sdd_composy_loop.py`
Interfaces:
  Consumes: iteration snapshots, diff identity, failing truths, and verdicts
  Produces: bounded correction task or `needs_human` with one exact reason
Steps:
- [ ] Add failing tests for identical diff, identical failure, scope drift, new architecture, destructive request, environment repetition, and third rejection.
- [ ] Run the focused test and observe failures.
- [ ] Implement progress fingerprints and stop classification.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
