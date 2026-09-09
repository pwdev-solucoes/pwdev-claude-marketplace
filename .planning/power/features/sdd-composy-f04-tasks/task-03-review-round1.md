# Task 03 review — round 1

STATUS: rejected

## SPEC

The round-1 corrections must defer Task 04 evidence/completion guards while
retaining Task 03 graph and lifecycle behavior. Tests must cover cycles, missing
dependencies, readiness/ordering, illegal transitions, blocker reasons, and
recovery. Starting a task must not bypass dependency safety; recovery must clear
stale diagnostic reasons.

## QUALITY

The focused suite now passes (`python3 -m unittest
tests/test_sdd_composy_tasks.py`: 10 tests). New tests exercise missing
dependencies, cycles, `next`, illegal transitions, blocker reasons, and removal
of blocker/rejection metadata. The implementation now rechecks dependency
completion for `ready -> running` and clears both reasons on recovery.

## FINDINGS

1. **P1 — Task 04 guards remain in Task 03.** `transition(..., target="complete")`
   still requires `tests_passed`, `qa_passed`, `review_approved`,
   `verify_approved`, and `trace_consistent`. This is the Task 04 evidence and
   completion contract, not a deferred implementation. It is also only boolean
   presence, with no fresh evidence records/timestamps. Remove/defer this guard
   until Task 04, or provide an explicitly approved scope change with the full
   evidence model.

2. **P2 — The start regression test is not adversarial.** It proves that a task
   with incomplete dependencies cannot start while pending, then marks it ready
   only after dependencies are complete. It does not mutate a ready task's
   dependency state and prove `ready -> running` rechecks it. Add that case so
   the claimed fix is protected against regression.

## REVIEW

Task 03 remains not approved. Graph/transition coverage and recovery cleanup
are improved, but the Task 04 completion guard is still prematurely coupled to
this task. No commit or HEAD movement was performed.
