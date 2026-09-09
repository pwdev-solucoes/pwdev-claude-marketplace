# Task 02 Review — Trace projection

## Disposition

CHANGES_REQUESTED

## Verification

- Ran `python3 -m unittest tests.test_sdd_composy_observability -v`: 8 tests passed.
- Ran `git diff --check`: passed.
- Read-only behavior is covered for summary/verify and the projection rebuild is byte-stable for the supplied graph.
- Graph construction rejects duplicate node IDs and dangling edge endpoints; the RF→US→SC→CA→TASK→TEST→EVIDENCE→MANIFEST→ARTIFACT→HASH→VERDICT chain is exercised.
- `source_event_count` and copied source events are emitted and bound during normal projection construction.

## Required fixes

1. `_projection_path()` validates the `trace` directory but does not reject a symlink at `trace/trace.json`. Consequently `query()` and `verify_projection()` can follow an attacker-controlled link outside the repository, and `build()` can replace the link rather than fail closed. Reject a symlink/non-regular projection target before read or publication.
2. `verify_projection()` only validates edge endpoints. It does not re-run node normalization/duplicate detection, so a manually tampered projection with duplicate IDs can be reported as valid. Verify the node set and links (and preferably projection hash) against the projection contract.
3. Add focused tests for: (a) source-event-count/events mismatch and read-only verification, (b) projection-target symlink rejection for query/build/verify, and (c) tampered duplicate node IDs or projection hash. Keep the evidence/artifact/hash/verdict chain assertion explicit.

No commit was created.
