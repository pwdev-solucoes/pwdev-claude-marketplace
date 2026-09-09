# Task 05 Review — cmux UI adapter

## Disposition

**REJECTED — Important findings remain.**

## Verification

- Read Task 05 brief and implementation report.
- `python3 -m unittest tests.test_sdd_composy_fleet -q` — 21 tests passed.
- `bash -n plugins/sdd-composy/scripts/fleet/ui-cmux.sh` — passed.
- Review was read-only; no HEAD movement or implementation changes were made.

## Findings

### Important — Required mocked cmux test matrix is absent

The brief explicitly requires failing mocked-CLI tests for unavailable cmux, workspace ownership, handle parsing, no foreign mutation, flash, stale handles, and fallback. The current fleet test file has no tests invoking `ui-cmux.sh`; its UI coverage only exercises headless/tmux and `fleet_select_ui`. The 21-test result therefore does not establish the Task 05 contract, especially command argument vectors, JSON handle parsing, ownership checks, status/flash, teardown, or foreign-mutation protection. Add executable tests for every required case and run them against the public shell functions.

### Important — cmux workspace ownership is not established at creation

`fleet_ui_cmux_start` creates a workspace with `new-workspace --json --name ... --cwd ...`, but it does not attach an explicit `sdd-composy` owner/marker or persist any ownership nonce. Later operations call `fleet_cmux_owned`, which accepts a workspace only when `list-workspaces --json` reports `sdd_composy: true` or `owner` equal to `sdd-composy`/`sdd_composy`. Unless the external cmux CLI automatically adds that marker (not guaranteed and not documented here), every workspace created by this adapter is rejected by its own status/flash/teardown operations. Define the ownership mechanism in the command vector/reference and test that a workspace created by the adapter can be operated, while an identically shaped foreign workspace cannot.

### Medium — fallback test does not cover the adapter override

The adapter supports `SDD_CMUX_BIN`, but `fleet_select_ui` only checks `command -v cmux`, so a mocked/overridden cmux binary is not selectable through `--ui cmux` unless it is literally named `cmux` on `PATH`. This is not necessarily a production defect, but it leaves the documented test seam disconnected from UI selection. Either document that the override is adapter-only and test direct invocation, or make selection honor the same override and test unavailable/fallback behavior.

## Required next action

Add the missing mocked CLI tests first, then resolve and document the ownership protocol. Re-run the fleet suite and request a fresh read-only review.
