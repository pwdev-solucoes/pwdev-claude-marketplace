# Task 04 — brief

Plan: .planning/power/features/sdd-composy-f07-loop/plan.md
Generated: 2026-09-09T11:13:42Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- The default autonomous loop limit is 3 iterations.
- Never let autonomous execution change approved requirements, stories, architecture, or scope.
- Stop on completion, iteration cap, no progress, scope expansion, architectural ambiguity, destructive action, external authorization, unrecoverable environment failure, or cancellation.
- A completion phrase is never proof; fresh `sdd-verify` evidence is required.
- Runtime-specific provider command vectors are built only in dedicated adapters.

## Task 04 — Runtime engines
Complexity: high
Files: `plugins/sdd-composy/scripts/loop-engine-codex.py`, `plugins/sdd-composy/scripts/loop-engine-claude.py`, `plugins/sdd-composy/templates/loop-result.schema.json`, `tests/test_sdd_composy_loop.py`
Interfaces:
  Consumes: one stage contract and registered repository root
  Produces: validated `{stage,status,message,verdict,evidence}` result for the orchestrator
Steps:
- [ ] Add failing vector, runtime-isolation, invalid-output, non-zero-exit, and timeout tests.
- [ ] Run the focused test and observe failures.
- [ ] Implement one fixed command-vector builder per runtime and strict result validation.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
