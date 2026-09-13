# Task 04 report

Status: DONE
Source: `.planning/power/features/pwdev-qa/task-04-brief.md`; `.planning/power/features/pwdev-qa/spec.md`
Date: 2026-09-12

## Delivered

- Added the `qa-specialist-strategy` contract for prioritized risk analysis, traceable coverage,
  entry/exit conditions, coverage gaps, and residual risk. Missing observable oracles remain
  `BLOCKED` instead of becoming invented coverage.
- Added the `qa-specialist-requirements` contract for clarity, testability, completeness,
  consistency, applicability, and traceability. It preserves criterion IDs and text and blocks
  ambiguous criteria without inventing thresholds or approvals.
- Added the `qa-specialist-functional` contract for positive, negative, boundary, and error
  partitions with explicit expected observable behavior. Missing error behavior remains
  `BLOCKED` for the contract owner.
- Kept all three specialists advisory: they do not execute workflows or tests, grant
  authorization, bind evidence, issue execution results, or derive global verdicts.
- Added two deterministic reference scenarios per specialist: one complete scenario and one
  failure or limitation scenario. The functional complete scenario contains the required
  positive, negative, and boundary partitions.

## Files changed

- `plugins/pwdev-qa/skills/qa-specialist-strategy/SKILL.md`
- `plugins/pwdev-qa/skills/qa-specialist-requirements/SKILL.md`
- `plugins/pwdev-qa/skills/qa-specialist-functional/SKILL.md`
- `tests/test_qa_specialists.py`

## TDD evidence

- Baseline: `python3 -m unittest tests.test_qa_core tests.test_qa_tooling
  tests.test_qa_runtime_contracts` — 21 tests passed before task changes.
- RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_specialists` — 7 tests ran
  with 9 assertion failures because all three required specialist files were absent.
- GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_specialists` — 7 tests
  passed.
- Regression: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_specialists
  tests.test_qa_core tests.test_qa_tooling tests.test_qa_runtime_contracts` — 28 tests passed.

## Scenario coverage

The tests parse the reference scenario tables and evaluate their fields deterministically. They
verify risk ordering and complete coverage, a blocking missing oracle, preservation of a clear
criterion, a verbatim ambiguous criterion with no invented threshold, a complete functional
positive/negative/boundary triplet, and a blocking error case without an expected observation.
Structural checks additionally enforce the common skill sections, shared contract links, and the
specialists' non-authorizing, non-executing boundary.

## Limitations

These tests exercise deterministic content and structure. They do not claim real-agent runtime
evaluation; that remains assigned to F05-24. No test, stored command, external effect, tool
installation, product correction, personal configuration change, publication, push, or merge was
performed by the specialist contracts.
