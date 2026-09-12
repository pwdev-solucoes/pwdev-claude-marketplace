# Task 08 — report

Status: COMPLETE
Task: F02-08 — Regressão, defeitos e produção
Date: 2026-09-12

## Delivered

- Added `qa-specialist-regression` with impact- and traceability-based selection, explicit
  inclusion/exclusion rationale, and a blocking convenience-only scenario.
- Added `qa-specialist-defects` with independent severity and priority, complete attempt history,
  evidence-backed terminal retesting, and `FAIL` for a proven current in-scope defect even when it
  has no associated criterion.
- Added `qa-specialist-production` with an exact explicit read-only authorization boundary,
  observation of approved existing telemetry only, no external effects, and prevention of
  recurrence linked to supported cause and reviewed evidence.
- Extended only `tests/test_qa_specialists.py` with deterministic success and limitation/failure
  scenarios while preserving all previous specialist assertions.

## TDD evidence

- RED: `python3 -m unittest tests.test_qa_specialists` — 33 tests ran with 9 expected failures
  because the three required skill files were absent.
- GREEN: `python3 -m unittest tests.test_qa_specialists` — 33 tests passed.
- F01/F02 regression: `python3 -m unittest tests.test_qa_core tests.test_qa_tooling tests.test_qa_runtime_contracts tests.test_qa_specialists`
  — 54 tests passed.
- Diff hygiene: `git diff --check` passed before staging; staged diff check repeated before commit.

## Limitations

- These specialist contracts are advisory. They execute no workflow, test, production query,
  remediation, deployment, message, or other external effect and grant no authorization.
- Agent-based reference-scenario evaluation remains assigned to F05-24, as required by the brief.
