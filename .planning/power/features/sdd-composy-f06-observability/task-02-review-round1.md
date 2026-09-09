# Task 02 Review — Trace projection (round 1)

## Disposition

CHANGES_REQUESTED

## Verification

- Ran `python3 -m unittest tests.test_sdd_composy_observability -v`: 11 tests passed.
- Ran `git diff --check`: passed.
- Projection target symlinks are now rejected for existing targets; duplicate IDs, source-event divergence, projection hash tampering, ordering, dangling links, and deterministic rebuild are covered.
- `verify_projection()` re-normalizes nodes/links and checks the canonical projection hash without writing.

## Remaining issue

`_projection_path()` still uses `path.exists()` before checking `is_symlink()`. A broken symlink at `trace/trace.json` therefore bypasses the safety check; `build()` can replace that symlink instead of failing closed. Use a lexists-style check (`path.is_symlink()` or `path.exists()`) and reject symlinks/non-regular targets independently, and add a regression test for a broken projection symlink across build/query/verify.

The tamper test should also assert bytes are unchanged across `verify_projection()` (the current `assertNotEqual` only proves the fixture was modified before verification).

No commit was created.
