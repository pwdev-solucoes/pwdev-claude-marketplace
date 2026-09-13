# Task 07 — report

Status: COMPLETE
Task: F02-07 — Segurança, automação e CI
Date: 2026-09-12

## Delivered

- Added `qa-specialist-security` with explicit target/method/environment/window authorization,
  reproducible findings, probe-based tooling, and a hard boundary between scanner output and
  penetration-test permission.
- Added `qa-specialist-automation` with isolated `playwright-cli` exploration, Playwright Test for
  repeatable CI suites, probe-based fallback, and evidence/reproduction-based flaky handling.
- Added `qa-specialist-cicd` with independent QA-verdict and export-status decisions; the QA gate
  reads the normalized manifest verdict and never derives it from exporter exit codes.
- Extended only the shared `tests/test_qa_specialists.py` contract with deterministic success and
  limitation scenarios while preserving all earlier specialist assertions.

## TDD evidence

- RED: `python3 -m unittest tests.test_qa_specialists` — 26 tests, 9 expected failures because the
  three required skill files were absent; 17 prior checks passed.
- GREEN: `python3 -m unittest tests.test_qa_specialists` — 26 tests passed.
- F01/F02 regression: `python3 -m unittest tests.test_qa_core tests.test_qa_runtime_contracts tests.test_qa_tooling tests.test_qa_specialists`
  — 47 tests passed.
- Diff hygiene: `git diff --check` passed before staging; staged diff check repeated before commit.

## Limitations

- These specialists are advisory contracts. They do not execute scanners, browsers, test suites,
  CI pipelines, exports, or external effects and do not grant authorization.
- Runtime scenario evaluation remains assigned to F05-24, as required by the task brief.

## Review correction — round 1

- Resolved the Important finding: `bounded-pentest` now carries owner, rate limit, stop
  conditions, and cleanup in addition to the preserved target, methods, environment, and window.
- Added one scenario for each missing operational boundary. Every omission keeps
  `execution=NOT_RUN`, `outcome=BLOCKED`, and never becomes `READY`.
- RED: focused suite ran 27 tests with 3 expected security-scenario failures before the fix.
- GREEN: focused suite passed 27 tests after the fix.
- Regression proof: temporarily reversing only the production fix reproduced the same 3 failures;
  restoring it returned the focused suite to 27 passing tests.
- F01/F02 regression: 48 tests passed across core, runtime contracts, tooling, and specialists.
- The deferred Minor quarantine finding was intentionally not changed in this round.
