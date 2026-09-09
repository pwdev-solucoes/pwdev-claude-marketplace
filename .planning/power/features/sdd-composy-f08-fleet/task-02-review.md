# Task 02 review — ports and isolated services

## Verdict

**REJECTED — implementation is not race-safe and rollback bookkeeping is incomplete.**

## Verification

`python3 -m unittest tests.test_sdd_composy_fleet -v` passed: 10 tests.

The focused suite covers invalid ranges, occupied slots, existing runtime files,
Compose absence, mode `0600`, and basic post-worktree cleanup. It does not cover
the required allocation race or complete rollback bookkeeping.

## Findings

### HIGH — lock is released immediately after `fleet_lock` returns

`fleet_lock` installs `trap 'rm -f "$lock"' RETURN`. A `RETURN` trap runs when the
function returns, so the lock created by `fleet_lock` is removed before the caller
enters the protected allocation section. The outer launch lock has the same issue.
Consequently two concurrent launches can both observe the same free slot and/or
interleave state publication. The required locked allocation race guarantee is not
implemented. Hold the lock for the caller's critical section and release it only
on explicit cleanup (including failure).

### MEDIUM — failed launch leaves partial fleet bookkeeping

`cleanup` removes the worktree, port marker, and generated `runtime.env`, but does
not remove the member records, `fleet.json`, or a copied Compose file created before
a later failure. A retry can therefore see stale records and a failed launch leaves
misleading central state. Rollback should remove only artifacts created by this
invocation (while preserving pre-existing state) or mark the fleet consistently as
failed/recoverable, as required by the task contract.

### MEDIUM — missing required race/rollback assertions

The task brief explicitly requires failing tests for allocation races and rollback
bookkeeping. The current 10-test file has no concurrent allocator test and does not
assert that member/fleet metadata and generated Compose state are handled after a
failure.

## Positive checks

- Invalid ranges and occupied marker slots fail closed.
- Existing `runtime.env` is refused without reading/adopting its contents.
- Generated runtime env is mode `0600` and contains only fleet variables.
- Compose absence fails closed and releases the allocated port/runtime env.
- Compose uses an isolated project name and loopback-only binding.
- Symlinked contracts/allowed paths are rejected.

## Required follow-up

Fix lock lifetime/ownership, add deterministic concurrent allocation coverage,
define and test complete rollback bookkeeping, then rerun the focused suite and a
fresh independent review.
