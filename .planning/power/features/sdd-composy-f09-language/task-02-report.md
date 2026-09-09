# Task 02 — Init integration report

## Result

Implemented language resolution in the shared init helper and documented the
Claude adapter contract. Init now resolves language before planning or writing
any project artifact.

## Contract covered

- `--lang pt-BR` and `--lang en-US` explicitly select and persist the language.
- Missing language on first init returns the resolver choices without writing.
- Invalid values return `invalid_language` without mutation.
- A persisted preference is reused on later init runs without prompting.
- Language is included in the plan metadata and plan token.
- Runtime adapters route the same `--lang` option; policy is not duplicated.

## Verification

```text
python3 -m unittest tests.test_sdd_composy_language
.........
Ran 9 tests in 0.047s
OK
```

`git diff --check` passed.

No commit was created.

## Review round 1 follow-up

Updated the existing runtime test fixture to model an explicit `--lang en-US`
selection for first-run `plan` and `apply` calls. Added a regression test that
invokes the real CLI without a language and verifies the choices response and
zero writes.

Full SDD Composy suite:

```text
python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'
Ran 276 tests in 12.050s
OK
```
