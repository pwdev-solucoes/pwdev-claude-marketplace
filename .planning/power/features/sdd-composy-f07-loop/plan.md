# SDD Composy F07 Autonomous Loop — Plan
Status: APPROVED
Spec: .planning/power/features/sdd-composy/spec.md
Updated: 2026-09-08

For agentic workers: execute this with pwdev-power:power-execute.

## Goal
Run a task through bounded autonomous execution, QA, required evidence publication, review, verification, and correction with durable resume and explicit stop reasons.

## Architecture
A provider-neutral loop state machine publishes each stage atomically. Runtime adapters invoke the current runtime without changing portable state. Successful durable stages are not repeated after resume.

## Tech Stack
Python 3 standard library, shell process control, structured JSON results, Python `unittest`.

## Global Constraints
- The default autonomous loop limit is 3 iterations.
- Never let autonomous execution change approved requirements, stories, architecture, or scope.
- Stop on completion, iteration cap, no progress, scope expansion, architectural ambiguity, destructive action, external authorization, unrecoverable environment failure, or cancellation.
- A completion phrase is never proof; fresh `sdd-verify` evidence is required.
- Runtime-specific provider command vectors are built only in dedicated adapters.

## File Structure
- `plugins/sdd-composy/scripts/{sdd_loop,loop-engine-codex,loop-engine-claude}.py`
- `plugins/sdd-composy/references/loop.md`
- `plugins/sdd-composy/templates/loop-result.schema.json`
- `plugins/sdd-composy/skills/sdd-loop/`
- `plugins/sdd-composy/commands/loop.md`
- `tests/test_sdd_composy_loop.py`

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

## Task 02 — Durable resume
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_loop.py`, `tests/test_sdd_composy_loop.py`
Interfaces:
  Consumes: persisted loop state plus task/trace evidence
  Produces: the exact next incomplete stage without replaying successful durable stages
Steps:
- [ ] Add failing interruption fixtures before/after each publication boundary.
- [ ] Run the focused test and observe failures.
- [ ] Implement artifact binding, stage evidence checks, and stale-state detection.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

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
