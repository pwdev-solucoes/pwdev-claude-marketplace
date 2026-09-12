# Task 09 report — fixture contract approval gate

Status: DONE

## Implementation

- Added a deterministic, read-only TASK-008 approval-bundle projection with canonical JSON and
  SHA-256 output.
- Added a CLI print path that performs no output, fixture, state, or budget writes.
- Required the exact projected SHA-256 before durable budget reservation and retained the exact
  runtime/UI authorization as a separate mandatory gate.
- Bound materialized task and phase approval artifacts to the explicit digest and provenance.
- Kept production calls and UI sessions behind injected fakes; no real acceptance run occurred.

## Verification

- RED: 4 focused tests failed on missing projection/gate behavior.
- Focused: 46 tests passed in 139.599s.
- Final full suite after the last gate change: 439 tests passed in 178.367s.

## Scope

Only the Task 09 smoke harness, its tests, and evidence/report were changed. The pre-existing
unstaged Hermes prompt parsing lines in the two smoke files remain excluded from this task's
commit. Preserved runtime resources and unrelated worktree changes were not modified.
