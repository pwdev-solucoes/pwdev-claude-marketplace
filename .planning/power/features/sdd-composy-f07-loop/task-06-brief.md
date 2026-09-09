# Task 06 — brief

Plan: .planning/power/features/sdd-composy-f07-loop/plan.md
Generated: 2026-09-09T11:20:56Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- The default autonomous loop limit is 3 iterations.
- Never let autonomous execution change approved requirements, stories, architecture, or scope.
- Stop on completion, iteration cap, no progress, scope expansion, architectural ambiguity, destructive action, external authorization, unrecoverable environment failure, or cancellation.
- A completion phrase is never proof; fresh `sdd-verify` evidence is required.
- Runtime-specific provider command vectors are built only in dedicated adapters.

## Task 06 — Loop skill and adapter
Complexity: high
Files: `plugins/sdd-composy/skills/sdd-loop/SKILL.md`, `plugins/sdd-composy/skills/sdd-loop/agents/openai.yaml`, `plugins/sdd-composy/commands/loop.md`, `tests/test_sdd_composy.py`, `tests/test_sdd_composy_loop.py`
Interfaces:
  Consumes: `sdd_loop.py start|status|continue|cancel`
  Produces: portable `$sdd-loop` and `/sdd-composy:loop`
Steps:
- [ ] Add failing discovery, autonomy disclosure, cancellation, and safe-stop tests.
- [ ] Run structural and loop tests.
- [ ] Implement skill, metadata, and thin adapter.
- [ ] Re-run structural and loop tests.
- [ ] Commit only when explicitly authorized.
