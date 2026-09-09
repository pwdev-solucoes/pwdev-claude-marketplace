# Task 04 Review — Headless and tmux UI adapters

## Disposition

REJECTED — round 1. The implementation is directionally sound, but the required
selection/fallback and teardown guarantees are not sufficiently demonstrated, and
headless teardown does not prove that the owned process has stopped.

## Verification

- `python3 -m unittest tests.test_sdd_composy_fleet -v` — 17 passed.
- `bash -n plugins/sdd-composy/scripts/fleet/*.sh` — passed.
- `git diff --check` — passed.

## Findings

1. **HIGH — required selection/fallback behavior has no test coverage.**
   `fleet_select_ui` in `scripts/fleet/common.sh` implements `auto`, `cmux`,
   `tmux`, and `headless`, but `test_sdd_composy_fleet.py` does not exercise
   explicit headless/tmux selection, cmux-present selection, cmux-missing fallback,
   auto fallback, or explicit tmux missing-tool failure. The brief explicitly
   requires selection and missing-tool fallback tests; the current 17-test suite
   only tests the tmux adapter's fake binary and collision.

2. **HIGH — headless teardown is not lifecycle-safe.**
   `ui-headless.sh` launches a background subshell and writes that shell PID to the
   handle. `fleet_ui_teardown` sends TERM to that PID, uses `wait` from the caller
   shell (which is not its parent), ignores the wait result, and removes the handle
   without verifying the process is gone. A provider that ignores TERM or survives
   the wrapper can remain running while the presentation handle is deleted. Add a
   deterministic teardown test with a long-lived helper and make teardown wait/poll
   for termination (and fail without deleting the handle when ownership cannot be
   proven), or otherwise document and test the chosen process-group semantics.

3. **MEDIUM — tmux teardown has no test.**
   The suite verifies tmux start/collision but never invokes `fleet_ui_teardown`,
   including its missing-tool/invalid-handle behavior and session cleanup.

4. **MEDIUM — launch selection is recorded but not exercised end-to-end.**
   `launch.sh` calls `fleet_select_ui` and records `ui`, yet the tests do not assert
   the persisted selected driver or verify that cmux is presentation-only. Add
   isolated fake PATH tests for the selection matrix and assert lifecycle metadata
   remains unchanged.

## Positive checks

- Command vectors use quoted `"$@"`; the headless test preserves spaces and the
  literal `$(literal)` argument, so no shell interpolation was observed.
- Both adapters reject symlink working directories and pre-existing/symlink handles.
- tmux session collisions fail closed and explicit tmux missing-tool behavior is
  implemented.
- Adapter handles contain presentation metadata only; core fleet records remain
  the lifecycle source of truth.
