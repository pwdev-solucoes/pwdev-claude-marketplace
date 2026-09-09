# Task 03 review

STATUS: rejected

## SPEC

Task 03 requires dependency graph validation (missing dependencies and cycles),
deterministic `next` selection, and legal `next`/`start`/`block`/`transition`
guards, including blocker reasons and rejected/blocked recovery. Task 04 owns
fresh evidence predicates and completion guards; those must not be claimed as
part of this task or implemented incompletely here. Task 02's contract remains
in force: unknown fields are preserved and updates are atomically published.

## QUALITY

The focused suite passes (`python3 -m unittest tests/test_sdd_composy_tasks.py`:
7 tests), and the graph validation and basic transition table are compact and
readable. Missing dependency and cycle checks run during load/transition, ready
tasks require completed dependencies, and JSON writes use the existing
same-directory atomic replacement. Unknown task/top-level fields survive
updates.

## FINDINGS

1. **P1 — Task 04 completion logic is implemented prematurely and is not fresh.**
   `transition(..., target="complete")` requires five boolean fields
   (`tests_passed`, `qa_passed`, `review_approved`, `verify_approved`,
   `trace_consistent`) even though evidence freshness, QA/review blocking,
   rejected verification, and valid completion are explicitly Task 04 scope.
   There are no evidence records or timestamps, so this cannot enforce the
   brief's “fresh” requirement and risks locking the Task 04 contract to an
   ad-hoc schema. Remove/defer the completion predicate to Task 04 (Task 03
   should reject/allow only its lifecycle transitions), or coordinate an
   explicit scope change and add the complete Task 04 evidence model.

2. **P1 — Required Task 03 acceptance tests are absent.** The seven focused
   tests cover templates plus Task 02 import/serialization only; they do not
   exercise cycles, missing dependencies, `next` ordering/readiness, illegal
   transitions, blocker reasons, or rejected/blocked recovery. Add executable
   tests for every item in the brief before approval.

3. **P2 — Recovery leaves stale blocker metadata.** `blocked -> ready` does not
   remove `blocked_reason`, so a task visibly ready can still carry an old
   blocker. Clear the blocker reason on recovery (and test it). Rejected
   recovery clears `rejection_reason`, which is the desired analogous behavior.

4. **P2 — `start` does not enforce readiness/dependency state.** `start` maps
   directly to `running`; only the state table prevents starts from pending.
   A task marked `ready` can have dependencies changed after publication and
   still start without rechecking them. Revalidate dependency completion on
   `ready -> running` (or explicitly guarantee immutable dependencies and test
   that invariant).

## REVIEW

Task 03 is not approved. Defer the Task 04 completion/evidence implementation,
add the missing focused transition/graph tests, clear blocker metadata during
recovery, and re-review. No commit or HEAD movement was performed.
