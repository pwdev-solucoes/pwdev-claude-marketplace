# Task 03 — Progress and correction limits

Status: IMPLEMENTED

## Scope

Added deterministic progress fingerprints and bounded correction classification to
`plugins/sdd-composy/scripts/sdd_loop.py`.

The classifier returns either a bounded `correction` with reason `progress`, or
`needs_human` with exactly one of: `identical_diff`, `identical_failure`,
`scope_drift`, `new_architecture`, `destructive_request`,
`repeated_environment_failure`, and `third_rejection`.

Safety and contract guards take precedence over apparent progress. Fingerprints
exclude timestamps and presentation metadata, so metadata-only changes cannot
masquerade as progress.

## Verification

Tests were added before implementation and initially failed because the new
interfaces were absent. After implementation:

```text
python3 -m unittest tests.test_sdd_composy_loop
Ran 18 tests ... OK
```

`git diff --check` also passed.

No commit was created.
