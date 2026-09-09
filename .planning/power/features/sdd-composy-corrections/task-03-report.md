# Task 03 — report

Status: implemented

## Scope

- Removed the implicit `en-US` fallback from `write_map`; an uninitialized repository now returns `NOT_INITIALIZED` without mutation even when the inventory is non-empty.
- Reused the real, localized and idempotent Task 02 init in successful map fixtures for both `pt-BR` and `en-US`.
- Excluded `.worktrees` and the selected output tree from mapping while preserving legitimate directories such as `src/worktrees`.
- Rejected output-directory symlinks, symlink ancestors and controlled publication destination symlinks before external reads or writes.
- Restored the companion publication regression: all documents are staged, prior files are restored after a replacement failure, and temporary files are removed.

## TDD evidence

- RED: focused map tests failed for non-empty uninitialized repositories, unstable repeated counts, symlink traversal and partial publication.
- GREEN: `python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v` — 55 tests passed in 2.555s.
- Static syntax check: `PYTHONPYCACHEPREFIX=/tmp/sdd-composy-task03-pycache python3 -m py_compile plugins/sdd-composy/scripts/sdd_map.py` — passed.
- Diff validation: `git diff --check` — passed.

## Environment note

The first `py_compile` attempt could not create Apple's default Python cache below `~/Library/Caches` because of the sandbox. The same check passed with `PYTHONPYCACHEPREFIX` confined to `/tmp`; this was an environment failure, not a test result.

## Review

The implementation remains within the three approved source/test files. Existing changes in `tests/test_sdd_composy_hermes.py` were preserved and excluded from the commit.

## Review round 1 corrections

- Preserved every unknown top-level field from the previous canonical `codebase.json`, while current known fields such as `schema`, inventory counts and staleness overwrite obsolete values.
- Replaced whole-document translation with language-selected static blocks rendered before commands, paths and domain evidence are interpolated. The regression proves `none observed/package.json` remains byte-identical in a `pt-BR` document.
- RED: the unknown-field regression failed with the extension absent; the dynamic-evidence regression failed with `nenhum observado/package.json`.
- GREEN: `python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v` — 57 tests passed in 1.953s.
- Syntax: `PYTHONPYCACHEPREFIX=/tmp/sdd-composy-task03-round1-pycache python3 -m py_compile plugins/sdd-composy/scripts/sdd_map.py` — passed.
- Diff validation: `git diff --check` — passed.
