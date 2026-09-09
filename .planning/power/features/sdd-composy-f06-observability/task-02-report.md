# Task 02 report — trace projection

Status: IMPLEMENTED — ROUND 2 FIXES APPLIED

Implemented deterministic trace projection in `scripts/sdd_trace.py`:

- `build` assembles normalized nodes and links for RF/US/SC/CA/task/test/evidence/manifest/artifact/hash/verdict identifiers.
- Duplicate and dangling IDs fail closed.
- Projection binds `source_event_count` and copies the validated source events.
- Publication uses a same-directory temporary file and atomic replace.
- `query` returns the complete projection or one node plus adjacent links.
- `verify-projection` checks event-count and event-source consistency without writes.
- Verification rejects symlink/non-regular projection targets, duplicate/tampered nodes,
  source-event divergence, invalid ordering, and projection-hash tampering.
- Broken projection symlinks are rejected via directory-entry checks, and byte-level
  immutability is covered for invalid and tampered projections.
- Rebuilds are byte-stable for the same source and graph.

Verification:

```text
python3 -m unittest tests.test_sdd_composy_observability -v
Ran 12 tests ... OK
git diff --check
```

No commit was created.
