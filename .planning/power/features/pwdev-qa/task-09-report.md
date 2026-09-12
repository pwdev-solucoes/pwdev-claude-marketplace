# Task 09 — report

Status: COMPLETE
Task: F02-09 — Métricas e prontidão
Date: 2026-09-12

## Delivered

- Added `qa-specialist-metrics` with explicit numerator, denominator, population, observation
  window/build snapshot, provenance, and treatment of every result state for each metric.
- Made a zero-applicable denominator explicitly `BLOCKED`, with no percentage and no implied
  `PASS`; distinguished requirements coverage from source-line coverage.
- Added `qa-specialist-readiness` with complete criteria and current-defect inventories, including
  unlinked defects, plus risks, limitations, evidence, and separately recorded human decisions.
- Applied verdict precedence exactly: a proven current in-scope failure is `FAIL`; pending work or
  zero applicable criteria is `BLOCKED`; `PASS` requires all applicable criteria passed and no
  current defects or pending risk/limitation.
- Kept both specialists advisory: readiness recommends but never approves or executes release.

## TDD evidence

- RED: `python3 -m unittest tests.test_qa_specialists` — 40 tests ran with 7 expected failures,
  all caused by the two absent specialist contracts.
- Additional RED after diff review: the focused zero-denominator test failed until its scenario
  carried the treatment of every result state, not only `NOT_APPLICABLE`.
- GREEN: `python3 -m unittest tests.test_qa_specialists` — 40 tests passed.
- F01/F02 regression: `python3 -m unittest tests.test_qa_core tests.test_qa_tooling tests.test_qa_runtime_contracts tests.test_qa_specialists`
  — 61 tests passed.
- Diff hygiene: `git diff --check` passed for the tracked task diff before staging and for the
  complete staged task diff before commit.

## Limitations

- Structural scenarios complement but do not replace the agent-based scenario evaluation assigned
  to F05-24.
- No workflow, evidence command, release, deployment, external effect, product correction, or
  human approval was executed by these advisory contracts.

## Review correction — round 1

- The positive metric scenario now materializes target, contract, collection source, freshness
  and build, all 10 criterion IDs, the 8 numerator IDs, the two remaining statuses/reasons,
  explicit N/A accounting, and evidence references.
- Nine isolated metric-precondition omissions each return `BLOCKED` with no percentage.
- The release-ready scenario now keeps the QA verdict and human decision record separate and
  exposes decision record, actor, authority, scope, rationale, and timestamp.
- Six isolated human-decision omissions each return `BLOCKED`; the specialist still only
  recommends and never grants or executes release approval.
- RED: the corrected focused suite ran 42 tests with 7 expected scenario-contract failures before
  implementation.
- GREEN: the corrected focused suite passed 42 tests.
- Regression proof: temporarily reversing both skill fixes made the four new focused contract
  tests fail; restoring the patch returned all 42 focused tests to green.
- F01/F02 regression: 63 tests passed across core, tooling, runtime contracts, and specialists.
- Diff hygiene: `git diff --check` passed after restoration.
