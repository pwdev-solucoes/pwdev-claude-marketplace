---
type: QA_REPORT
okf_version: "0.2"
title: "F05 Task 01 execution contract"
lifecycle:
  status: DRAFT
  human_approval: PENDING
sources:
  - .planning/power/features/sdd-composy-f05-quality/task-01-brief.md
generated:
  by: codex
  at: 2026-09-09T00:00:00Z
verified:
  - by: codex
    at: 2026-09-09T00:00:00Z
    event: focused-tests
---

# Verification report

Implemented the F05 Task 01 execution contract reference, portable skill,
OpenAI metadata, Claude thin adapter, and focused contract tests. The contract
defines dependency preflight, TDD RED evidence, allowed-path enforcement, real
verification command evidence, environment ownership and cleanup, sanitized
SHA-256 manifests, and guarded transitions to `qa_required`, `blocked`, or
`rejected`.

## Commands and output

1. RED check before implementation:

   `python3 -m unittest tests.test_sdd_composy_quality`

   Result: `FileNotFoundError` for the not-yet-created execution reference,
   skill, metadata, and adapter (5 errors). This confirmed the tests exercised
   missing behavior rather than passing accidentally.

2. Focused green verification:

   `python3 -m unittest tests.test_sdd_composy_quality`

Result: `Ran 5 tests in 0.002s` / `OK`.

Round-1 behavioral verification:

`python3 -m unittest tests.test_sdd_composy_quality`

Result: `Ran 9 tests in 0.003s` / `OK`. Tests exercise dependency, TDD, path,
command evidence/hash/sanitization, environment, cleanup, and guarded
transition outcomes through the public `sdd_execute` boundary.

Round-2 behavioral verification:

`python3 -m unittest tests.test_sdd_composy_quality`

Result: `Ran 10 tests in 0.001s` / `OK`. Added regression coverage for exact
`ready` state, explicit human approval, empty evidence blocking, required result
fields, confined relative/non-symlink evidence paths, and deterministic guarded
outcomes.

3. Formatting verification:

   `git diff --check`

   Result: no output, exit 0.

No commit was created. Review and human approval remain required before merging
this task into the phase ledger.
