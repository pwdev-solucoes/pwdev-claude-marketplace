# Task 05 — brief

Plan: .planning/power/features/sdd-composy-f07-loop/plan.md
Generated: 2026-09-09T11:16:16Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- The default autonomous loop limit is 3 iterations.
- Never let autonomous execution change approved requirements, stories, architecture, or scope.
- Stop on completion, iteration cap, no progress, scope expansion, architectural ambiguity, destructive action, external authorization, unrecoverable environment failure, or cancellation.
- A completion phrase is never proof; fresh `sdd-verify` evidence is required.
- Runtime-specific provider command vectors are built only in dedicated adapters.

## Task 05 — Loop orchestrator
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_loop.py`, `plugins/sdd-composy/scripts/loop-engine-codex.py`, `plugins/sdd-composy/scripts/loop-engine-claude.py`, `tests/test_sdd_composy_loop.py`
Interfaces:
  Consumes: state-machine stage and runtime-engine result
  Produces: sequential execute/QA/evidence/review/verify run with task and trace publications
Steps:
- [ ] Add failing lifecycle tests for approval, one correction, cap exhaustion, cancellation, and resume.
- [ ] Run the focused test and observe failures.
- [ ] Implement orchestration using the canonical skill result contracts.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
