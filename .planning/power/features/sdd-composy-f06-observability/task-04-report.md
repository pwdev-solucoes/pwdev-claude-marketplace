# Task 04 report

## Implementation

Added `scripts/sdd_status.py`, a read-only consolidated status projection. It
aggregates config, global state, task Markdown, trace integrity, loop records,
and fleet records with per-source confidence and a conservative exact
`next_action`. Malformed inputs fail closed and no source is repaired or
written. Added the OKF reference at `references/status.md`.

## Verification

`PYTHONDONTWRITEBYTECODE=1 python3` import/smoke check passed for an empty
repository and returned `uninitialized` with `run sdd-init`.

## Notes

Added the focused status contract matrix to
`tests/test_sdd_composy_observability.py`, covering canonical statuses, malformed
Markdown and symlink inputs, JSON/text CLI output, deterministic output, and
byte-level read-only behavior. Task scanning now reports malformed and unsafe
symlink sources instead of silently ignoring them.

Focused verification: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sdd_composy_observability -q` — 16 tests passed.
