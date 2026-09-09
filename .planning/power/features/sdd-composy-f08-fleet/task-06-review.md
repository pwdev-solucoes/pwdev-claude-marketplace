# Task 06 review

## Disposition

REJECTED — important isolation gap remains in the cmux presentation boundary.

## Verification

- `python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_observability` — 46 tests passed.
- `bash -n plugins/sdd-composy/scripts/fleet/dashboard.sh` — passed.
- The implemented dashboard rejects malformed member JSON/symlinks, bounds messages, emits repository-confined display paths, aggregates member states deterministically, and marks failed/blocked/cancelled or transitioned members for attention.
- `sdd_status.py` is read-only and emits deterministic source/confidence fields and next actions; the fleet and trace precedence paths exercised by the suite passed.

## Important finding

`ui-cmux.sh` proves only the generic `owner: sdd-composy` marker before mutating a workspace. It does not bind the handle to the fleet that created it, and the handle contains no fleet identifier. Consequently, a handle for a different sdd-composy fleet (or a forged handle pointing at any workspace carrying the generic owner marker) can pass `fleet_cmux_owned` and receive `set-status`, `flash`, or `close-surface` calls. This violates the exact F08 global constraint that cmux operations are restricted to the workspace created by *this fleet*.

The fix should establish and persist a fleet-specific ownership marker (for example `fleet_id`/`sdd_composy_fleet`) at workspace creation, include the fleet id in the handle, and require that same marker in every status/flash/teardown validation. Add a regression test with two distinct fleet ids, plus a forged/mismatched-handle case, before re-review.

## Scope notes

No lifecycle mutation was observed in dashboard/status/cmux paths. The issue is limited to presentation workspace isolation; it is not safe to approve until corrected because teardown is also a mutating operation.
