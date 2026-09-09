# F07 Task 05 — Loop orchestrator

## Status

IMPLEMENTED — round 1 fixes

## Scope

Added provider-neutral `sdd_loop.orchestrate`, requiring explicit human approval and executing canonical EXECUTE → QA → EVIDENCE → REVIEW → VERIFY stages. Successful stage results are durably published before task/trace callbacks are emitted. Failed results emit no publication, correction is bounded by the iteration cap and safety guards, cancellation is supported, and an existing loop resumes from its first unpublished stage without replaying durable work.

## Verification

`python3 -m unittest tests.test_sdd_composy_loop` — 24 tests passed.

Lifecycle coverage includes approval, canonical ordering/publication, failure with no publication, cap exhaustion, cancellation, and resume.

`git diff --check` passed.

No commit created.
