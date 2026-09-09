# Task 04 — Headless and tmux UI adapters

## Result

Implemented presentation-only headless and tmux adapters with explicit UI-driver
selection and fallback. Headless launches a detached argv vector and returns a
recoverable PID handle; tmux creates an isolated session and returns a session
handle. Both reject unsafe working directories, handle collisions, and preserve
argument boundaries without shell interpolation. Teardown consumes only the
adapter handle and does not alter fleet lifecycle records.

`launch.sh --ui auto|cmux|tmux|headless` now records the selected presentation
driver. `auto`/`cmux` fall back to tmux and then headless when unavailable;
explicit `tmux` fails closed if tmux is missing.

## Verification

- `bash -n plugins/sdd-composy/scripts/fleet/*.sh` — passed.
- `python3 -m unittest tests.test_sdd_composy_fleet -v` — 17 tests passed.
- `git diff --check` — passed.

No commit created.

## Round 1 fixes

- Added behavioral coverage for the complete UI selection matrix, including
  explicit and automatic fallback behavior.
- Headless teardown now polls for process disappearance and retains the handle
  when ownership cannot be proven.
- Added mocked tmux teardown coverage and launch-level persistence checks proving
  the selected UI does not alter member lifecycle state.
- `python3 -m unittest tests.test_sdd_composy_fleet -q` — 21 tests passed.
- `bash -n plugins/sdd-composy/scripts/fleet/*.sh` and `git diff --check` passed.
