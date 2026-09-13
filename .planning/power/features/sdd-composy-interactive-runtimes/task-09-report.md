# Task 09 report — fixture contract approval gate

Status: DONE

## Implementation

- Added a deterministic, read-only TASK-008 approval-bundle projection with canonical JSON and
  SHA-256 output.
- Added a CLI print path that performs no output, fixture, state, or budget writes.
- Required the exact projected SHA-256 before durable budget reservation and retained the exact
  runtime/UI authorization as a separate mandatory gate.
- Bound materialized task and phase approval artifacts to the explicit digest and provenance.
- Expanded the canonical approval object to cover every load-bearing approved Task 08/global
  constraint; the task record and phase artifacts embed this same complete object.
- Kept production calls and UI sessions behind injected fakes; no real acceptance run occurred.

## Verification

- RED: 4 focused tests failed on missing projection/gate behavior.
- Focused: 46 tests passed in 139.599s.
- Corrected original committed-head result from independent review: 438 tests passed in 177.370s.
- Review-fix RED: complete-contract coverage was absent and the old narrow digest reached the
  provider boundary.
- Review-fix focused: 6 tests passed in 2.279s; smoke module: 48 tests in 143.129s.
- Final clean detached `5f6e407` suite: 440 tests passed in 177.987s using the exact recorded
  discovery command.
- Review-fix round 2 RED: omitted public UI, JSON publication, and implementation-boundary
  clauses; the prior digest still reached the fake provider.
- Review-fix round 2 focused: 7 tests passed in 2.148s; smoke module: 49 tests in 141.858s.
- Final clean detached `59de30c` suite: 441 tests passed in 189.521s using the exact recorded
  discovery command.

## Scope

Only the Task 09 smoke harness, its tests, and evidence/report were changed. The pre-existing
unstaged Hermes prompt parsing lines in the two smoke files remain excluded from this task's
commit. Preserved runtime resources and unrelated worktree changes were not modified.
