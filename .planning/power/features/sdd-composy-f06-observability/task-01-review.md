# Task 01 review

## Verdict: CHANGES_REQUESTED

The focused suite passes (`python3 -m unittest tests.test_sdd_composy_observability`, 5 tests), and the implementation correctly provides a disabled no-op, validates semantic event fields recursively (including prohibited keys), rejects malformed JSONL and symlinked trace targets, preserves existing lines, assigns deterministic sequence/IDs, and keeps `events`, `summary`, and `verify` read-only. The reference documents the append-only/no-repair contract and restrictive modes.

One requirement is not fully met:

* **MEDIUM — existing trace directories are not mode-restricted.** `_target(..., create=True)` calls `chmod(0700)` only inside `if create` after `mkdir(..., exist_ok=True)`, but the code path for an already-existing regular `trace/` directory leaves its prior mode unchanged. Since the task explicitly requires mode-restricted append and the reference promises that the trace directory is mode `0700`, normalize an existing regular directory to `0700` before append (and add a regression test that starts with a permissive directory mode). The file is normalized to `0600` after append, but the parent-directory gap remains.

Please fix the root cause and add the regression test before re-review. Do not alter or repair an invalid JSONL trail.

