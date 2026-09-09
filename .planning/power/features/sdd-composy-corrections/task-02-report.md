# Task 02 — execution report

Status: DONE

## Baseline preserved

- `tests/test_sdd_composy_hermes.py` was already modified before this task recovery.
- The file was neither edited nor staged and is excluded from the task commit.
- Existing Task 01 changes in `sdd_status.py` and its operational JSON-authority contract were not changed.

## Implementation

- Added `sdd_localization.py` to localize plugin-owned static governance template text for `pt-BR`, while preserving `en-US` exactly.
- Changed initialization to localize templates before interpolating runtime values, preventing project names, commands, IDs, paths, or user evidence from being translated by textual collision.
- Made initialization publish an exact `created` list and retain an empty list on idempotent reapplication.
- Added `.claude` compatibility handling for a correct symlink, an existing directory with a coherent bridge file, and conflicts.
- Added valid schema-v1 `INIT` state publication only after a conflict-free generation.
- Existing state is validated before any publication, preserved verbatim (including unknown fields), and never overwritten.
- Verification now requires valid persisted language and valid state, with `reconcile_init_state` for legacy/missing state.
- Symlink destination and ancestor checks, atomic writes, and conflict preservation remain enforced.

## TDD evidence

- RED: conflicted apply published `.planning/sdd-composy/state.json`; new regression test failed.
- GREEN: state publication is now suppressed while mandatory conflicts remain.
- RED: malformed existing state was detected only after governance files were published; new regression test failed.
- GREEN: state authority is validated before any project mutation.
- RED: dynamic value `Never read .env / TASK-777 / ## Context` was translated after interpolation; new regression test failed.
- GREEN: localization now runs before runtime interpolation and the value remains exact.

## Verification

- `python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v`
  - Result: PASS, 47 tests.
- `python3 -m py_compile ...` initially hit an environment-only `PermissionError` because the system Python cache target was outside the writable sandbox. The retry uses an explicit cache directory under `/tmp`.
- `git diff --check`
  - Result: PASS when run with the final verification command.

## Review result

- Initial review (`task-02-review.md`) found four Important issues; correction round 1 addressed all four:
  1. Replaced fragment substitution with complete pt-BR governance documents while preserving dynamic placeholders.
  2. Added plan-time ancestor-symlink refusal before destination inspection.
  3. Expanded state validation to the relevant complete schema contract: nullable patterns, gate shape/enums/actor/date, summary arrays, strict integer/range checks, and timestamp format.
  4. Added structured partial-publication failure results with exact `created`, ordered `pending`, conflicts, actor, and error; regression covers failure on the third publication.
- Fresh correction verification: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v` — PASS, 50 tests.
- `py_compile` with cache under `/tmp` and `git diff --check` — PASS.

## Correction round 2

- Re-review 1 identified that structured partial-publication reporting ended after the document loop.
- `apply()` now builds one ordered publication inventory and applies the same structured error contract across document files, directory setup, `.claude` symlink/bridge, language persistence, and state publication.
- Regression at `os.symlink`: seven created documents are retained and reported; `.claude` and `state.json` are the exact pending steps.
- Regression at late state publication: documents, compatibility link, and language config remain reported as created; only `state.json` remains pending.
- Fresh verification: 52 focused tests PASS; `git diff --check` PASS.
