---
type: REVIEW_REPORT
okf_version: "0.2"
title: "F05 Task 06 lifecycle integration review"
sources:
  - resource: ".planning/power/features/sdd-composy-f05-quality/task-06-brief.md"
  - resource: ".planning/power/features/sdd-composy-f05-quality/task-06-report.md"
  - resource: "plugins/sdd-composy/scripts/sdd_tasks.py"
  - resource: "tests/test_sdd_composy_tasks.py"
  - resource: "tests/test_sdd_composy_quality.py"
generated:
  by: "f05_task06_review"
  at: "2026-09-09"
verified:
  - by: "f05_task06_review"
    event: "focused-quality-and-task-tests"
lifecycle:
  status: REJECTED
  human_approval: PENDING
  transition: rejected
---

# F05 Task 06 — review

## Verification

| Command | Result |
|---|---|
| `python3 -m unittest tests.test_sdd_composy_quality tests.test_sdd_composy_tasks` | PASS (58 tests) |
| `git diff --check` | PASS |

## Findings

1. **Important — integration is not failure-atomic.** `integrate_quality_artifacts()` writes the synthetic `qa`, `review`, `verify`, and `trace` evidence into the task before running the guarded transition chain. If a later guard fails (for example, a stale or otherwise invalid task projection), the function raises after mutating the caller's `data`. The brief requires guarded lifecycle transitions and says rejected or pending approvals must not mutate task state. Validate the complete transition on a copy, or stage and commit the projection only after every guard succeeds; add a regression test asserting byte/value equality on failure.

2. **Important — the required end-to-end rejection matrix is incomplete.** The tests cover one rejected QA artifact and one missing human approval, but do not exercise each rejection path across `running -> qa_required -> evidence_required -> review_required -> verify_required -> complete` (rejected QA, rejected review, non-COMPLETE verdict, missing artifact, and pending human approval at each consumed artifact). Add focused tests that assert the state and evidence remain unchanged for every rejected/pending input.

3. **Minor — artifact predicates are narrower than the report contract.** Integration only checks `lifecycle.status`, `human_approval`, and the verdict enum; it does not verify that QA/review/verdict artifacts contain their expected report type or verification actor metadata. This may be intentional for a thin bridge, but the task says it consumes verified artifacts and the quality contract requires those predicates. Either enforce the minimal contract here or document/test that upstream loaders are the authority.

## Disposition

**REJECTED** pending fixes for findings 1 and 2. The focused test modules are green, but that does not establish failure atomicity or the required end-to-end rejection coverage.
