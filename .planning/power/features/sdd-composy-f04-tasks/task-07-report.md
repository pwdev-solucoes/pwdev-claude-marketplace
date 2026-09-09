# Task 07 completion report

## Outcome

Implemented guarded explicit synchronization apply in `sdd_sync.py`. Apply requires
the exact `CONFIRM-SDD-SYNC` token, validates the plan schema and input fingerprints,
rejects stale or malformed inputs and symlink destinations, supports explicit
`markdown` and `json` authority choices, preserves unknown JSON fields, writes via
same-directory atomic replacement, and performs post-apply read-only verification.

## Tests

Added tests for stale plans, changed inputs, exact token, explicit Markdown authority,
explicit JSON authority, symlink destinations, and post-apply verification.

Commands and results:

```text
python3 -m unittest tests.test_sdd_composy_tasks -q
Ran 24 tests in 0.477s
OK

git diff --check
OK (no output)
```

No commit was created.
