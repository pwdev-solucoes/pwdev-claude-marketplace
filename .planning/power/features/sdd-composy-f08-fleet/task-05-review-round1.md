# Task 05 Review — cmux adapter — Round 1

## Disposition

**REJECTED.** The ownership implementation was adjusted, but the required behavioral test evidence is still absent.

## Verification

- Read-only review; no HEAD movement or implementation changes.
- `python3 -m unittest tests.test_sdd_composy_fleet -q` — 21 tests passed.
- `bash -n plugins/sdd-composy/scripts/fleet/ui-cmux.sh` — passed.

## Findings

### Important — Required mocked-CLI tests still do not exist

`tests/test_sdd_composy_fleet.py` still contains no test invoking `ui-cmux.sh` or its functions. The only cmux-related assertions remain the selection matrix, which checks `fleet_select_ui` with a filename on `PATH`; it does not exercise mocked cmux operations. There is no evidence for handle parsing, ownership marker creation, foreign workspace rejection, stale/malformed handles, status decoration, flash, teardown, no foreign mutation, unavailable cmux, or fallback through `SDD_CMUX_BIN`. The 21-test suite therefore remains insufficient for Task 05’s explicit acceptance criteria.

### Important — Ownership marker command is unverified and undocumented

The adapter now calls `set-workspace-meta --workspace <id> --owner sdd-composy --fleet-driver cmux`, which is a reasonable explicit ownership protocol, but neither `references/cmux.md` nor an executable mocked CLI test specifies or verifies this command vector. A compatibility regression in the cmux command shape would go undetected. Add a fake CLI that records arguments and returns deterministic JSON, assert the marker call occurs before handle publication, then prove owned status/flash/teardown and rejection of foreign/stale handles.

### Medium — SDD_CMUX_BIN selection change is untested

`fleet_select_ui` now honors `SDD_CMUX_BIN`, but the existing selection test does not set that environment variable. Add assertions for an override path, unavailable override fallback, and requested `cmux` behavior when tmux/headless are available.

## Required next action

Add the complete mocked CLI behavior matrix and document the ownership command protocol. Re-run the fleet suite and request another independent review.
