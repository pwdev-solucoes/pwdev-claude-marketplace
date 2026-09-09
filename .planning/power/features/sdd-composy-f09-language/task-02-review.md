# Task 02 Review

## Disposition

**REJECTED — important regression in the existing init runtime contract.**

## Scope checked

- Task brief and F09 specification.
- `sdd_init.py`, `sdd_language.py`, init skill and command adapter.
- New language integration tests.
- Existing runtime/structural tests.

## Findings

### Important — existing init runtime tests and callers now receive a prompt instead of a plan

The new resolver correctly makes an omitted language return `{"choices": ["pt-BR", "en-US"]}` before artifact planning, but the existing runtime test suite still invokes `plan`/`apply` without `--lang`. As a result, the repository-wide SDD Composy suite no longer passes: 1 failure and 7 errors in `tests.test_sdd_composy_runtime` (275 tests executed). Those tests attempt to read `actions`, `conflicts`, and `plan_token` from the prompt response, and no artifacts are created.

This is expected behavior for a fresh uninitialized workspace under the new contract, so the implementation should not silently restore a default. The test/caller fixtures need to model the init interaction by passing an explicit language on the first `plan`/`apply` (or performing a language-selection step), while retaining dedicated tests that assert omission prompts and writes nothing. The full suite must be green before Task 02 is approved.

## Positive checks

- `--lang pt-BR` and `--lang en-US` are accepted and persisted.
- Invalid language returns `invalid_language` without creating `.planning`.
- Missing language on first init returns choices without generating artifacts.
- Persisted language is reused without prompting.
- Consumer resolution is read-only and returns `not_initialized` before init.
- Language and source are included in the plan and recomputed plan token.
- Policy is centralized in `sdd_language.py`; adapters only expose/pass the option.

## Commands run

```text
python3 -m unittest tests.test_sdd_composy_language -v
9 tests passed

python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'
FAILED: 275 tests; 1 failure, 7 errors
```

`git diff --check` passed.

## Required disposition

Update the existing runtime tests/fixtures (without weakening the new no-language prompt contract), run the focused and complete SDD Composy suites again, and submit a fresh review.
