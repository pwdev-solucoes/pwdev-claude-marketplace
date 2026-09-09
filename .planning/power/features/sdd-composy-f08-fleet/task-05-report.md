# Task 05 — cmux UI adapter

## Result

Added the presentation-only cmux adapter and reference. It records deterministic
workspace/surface handles, validates plugin ownership before status, flash, and
teardown operations, rejects stale/foreign handles, and never changes fleet
lifecycle truth. cmux absence remains covered by the existing selection fallback
to tmux/headless.

## Verification

- `bash -n plugins/sdd-composy/scripts/fleet/ui-cmux.sh` — passed.
- `python3 -m unittest tests.test_sdd_composy_fleet -q` — 21 tests passed.
- No commit created.

## Notes

The adapter accepts an override through `SDD_CMUX_BIN`, which permits a mocked
CLI in integration tests without changing production behavior.

## Round 1 fixes

- UI selection now honors `SDD_CMUX_BIN` for both explicit `cmux` and `auto`.
- New workspaces receive an explicit `sdd-composy` ownership marker before a
  surface handle is persisted.
- Subsequent status, flash, and teardown calls validate that marker and refuse
  foreign or stale handles.
- `bash -n plugins/sdd-composy/scripts/fleet/*.sh`, the fleet test suite (21
  tests), and `git diff --check` pass.

## Round 2 fixes

- Added a mocked cmux CLI matrix covering JSON handle parsing, ownership marker
  creation, status, flash, teardown, foreign/stale handle refusal, and mutation
  isolation.
- Added tests for `SDD_CMUX_BIN` selection and override behavior.
- Documented the `set-workspace-meta` ownership protocol.
- `python3 -m unittest tests.test_sdd_composy_fleet -q` — 23 tests passed.
