# Task 06 — implementation report

Status: DONE

## Scope delivered

- Added `qa-specialist-data` with distinct reconciliation, integrity, transaction, and atomicity
  oracles; reconciliation/integrity cannot stand in for rollback/partial-write observations.
- Added `qa-specialist-accessibility` with scanner, keyboard, focus, semantic, visual, and
  assistive-technology boundaries; a clean scanner result alone remains `BLOCKED`.
- Added `qa-specialist-performance` with bounded load authorization, probe-based tooling,
  contextual sample/percentile reporting, and no approval from an isolated average.
- Extended the shared specialist behavioral test with success and limitation scenarios for all
  three skills while preserving the established advisory contract and status vocabulary.

## TDD evidence

- RED: `python3 -m unittest tests.test_qa_specialists` ran 20 tests and failed 9 because the three
  required specialist files were absent. Existing specialist behaviors remained green.
- First GREEN attempt: 20 tests ran with 1 structural failure caused by a line break in the exact
  `cannot grant authorization` contract phrase for performance.
- GREEN after minimal correction: `python3 -m unittest tests.test_qa_specialists` ran 20 tests in
  0.005s — `OK`.
- Review fix round 1 RED: after tests required row-level authorization scope, the focused suite
  ran 20 tests and failed 4 because the data and performance scenario tables lacked those fields.
- Review fix round 1 GREEN: after the minimum table changes, the focused suite ran 20 tests in
  0.005s — `OK`.
- Regression proof: temporarily reverting only the two table fixes restored exactly the 4 new
  failures; restoring them returned the focused suite to 20 tests in 0.006s — `OK`.

## Regression and checks

- `python3 -m unittest tests.test_qa_core tests.test_qa_runtime_contracts tests.test_qa_tooling tests.test_qa_specialists`
  ran 41 tests in 0.053s after review fix round 1 — `OK`.
- `git diff --check` — passed with no output.
- No ledger, brief, review, reference-plugin, runtime configuration, installation, publication,
  push, or merge was changed by this task.

## Limitations

- These deterministic structural/behavioral scenarios complement but do not replace the F05-24
  agent evaluation required by the brief.
- No real database, accessibility, assistive-technology, or load execution was performed. Such
  execution depends on observed probes, safe data/access, and applicable explicit authorization.
- Reference observations now become `READY` only when the same row carries the complete bounded
  authorization context. Each omitted component is demonstrated as `NOT_RUN`/`BLOCKED`.

## Files

- `plugins/pwdev-qa/skills/qa-specialist-data/SKILL.md`
- `plugins/pwdev-qa/skills/qa-specialist-accessibility/SKILL.md`
- `plugins/pwdev-qa/skills/qa-specialist-performance/SKILL.md`
- `tests/test_qa_specialists.py`
- `.planning/power/features/pwdev-qa/task-06-report.md`
