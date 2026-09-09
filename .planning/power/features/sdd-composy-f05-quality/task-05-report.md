---
type: VERIFICATION_REPORT
okf_version: "0.2"
title: "F05 Task 05 verification contract"
sources:
  - resource: ".planning/power/features/sdd-composy-f05-quality/task-05-brief.md"
  - resource: "tests/test_sdd_composy_quality.py"
generated:
  by: "f05_task05"
  at: "2026-09-09"
verified:
  - by: "f05_task05"
    event: "focused-contract-tests"
lifecycle:
  status: APPROVED
human_approval: PENDING
transition: verify_required
---

# F05 Task 05 — Verification contract

Implemented the OKF verdict template, verification reference, portable
`sdd-verify` skill, and Codex metadata. The contract requires fresh independent
commands, active refutation of claims, stale-evidence rejection, SHA-256 and
confined paths, explicit environment-failure classification, and fail-closed
`COMPLETE`/`REJECTED` outcomes.

Round 1 review correction: the DRAFT/PENDING template now defaults to the
non-terminal `verify_required` transition. Only a completed verification gate
may replace it with `complete` or `rejected`.

## Verification evidence

| Command | Result |
|---|---|
| `python3 -m unittest tests.test_sdd_composy_quality.ExecutionContractTest.test_verification_template_declares_truth_table_and_verdict_values tests.test_sdd_composy_quality.ExecutionContractTest.test_verification_reference_requires_independent_fresh_refutation_and_stale_rejection tests.test_sdd_composy_quality.ExecutionContractTest.test_verification_skill_is_portable_and_fails_closed tests.test_sdd_composy_quality.ExecutionContractTest.test_verification_runtime_metadata_routes_shared_skill` | PASS (4 tests) |
| `git diff --check` | PASS |

No commit was created.
