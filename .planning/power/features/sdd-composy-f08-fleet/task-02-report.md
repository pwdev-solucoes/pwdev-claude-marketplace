# Task 02 — ports and isolated services report

## Result
Implemented locked deterministic port allocation and isolated Compose startup for fleet launches.

## Changes
- Added locked port-slot allocation with configurable validated range and occupied-slot checks.
- Added mode-restricted generated `runtime.env`; existing runtime files are never adopted.
- Added fleet Compose template with loopback-only port binding and project isolation.
- Added Compose fail-closed validation and rollback of worktree, allocation marker, and generated runtime state.
- Recorded allocated port in each member record.

## Verification
`python3 -m unittest tests.test_sdd_composy_fleet` — 10 tests passed.
`git diff --check` — passed.

No commit created.

## Round 1 follow-up
- Corrected lock lifetime: allocation and launch critical sections now release only explicitly after cleanup/publication.
- Added concurrent allocator coverage proving distinct slots under contention.
- Failure cleanup now removes invocation-created member/fleet metadata and Compose artifacts in addition to worktree, port, and runtime state.
- Focused suite: `python3 -m unittest tests.test_sdd_composy_fleet -v` — 12 tests passed.

## Round 2 follow-up
- Rollback now snapshots pre-existing fleet/member state and refuses overwrite of existing Compose state.
- Existing `fleet.json`, member records, Compose files, and runtime files remain byte-for-byte untouched on failure.
- Added regression coverage for pre-populated metadata and failure injection.
- Focused suite: 13 tests passed.

## Round 3 follow-up
- Publication now refuses any pre-existing `members/<task-id>.json` destination before writing.
- Added isolated regression coverage for member-only state without `fleet.json`, asserting byte-for-byte preservation.
- Focused suite: 14 tests passed.

## Round 4 follow-up
- Member destinations are now fully preflight-validated before any member or fleet state is written.
- Added mixed multi-task collision regression proving zero partial records and exact preservation of the colliding member.
- Focused suite: 15 tests passed.
