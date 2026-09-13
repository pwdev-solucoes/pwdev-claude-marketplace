# Task 10 — report

Status: DONE
Task: F03-10 — Schema e validação de entrada
Date: 2026-09-12

## Delivered

- Added the version 1 report-manifest JSON Schema with required structures, exact known enums,
  strict scalar types, extension preservation, collection limits, and the declared 10 MiB
  evidence-size limit.
- Added the importable stdlib-only Python 3.9 contract: `ValidationError(ValueError)`,
  `validate_manifest(data: dict) -> dict`, and `load_manifest(path: Path) -> dict`.
- Validation rejects boolean-as-integer values, malformed or timezone-free timestamps, duplicate
  IDs/references/JSON fields, unresolved references, invalid retest histories, unsafe paths,
  invalid hashes and enums, oversized collections, evidence declarations, and manifest files.
- Valid manifests are returned as independent deep copies. Unknown fields remain intact in the
  normalized manifest but are not copied into or exposed through any automatic public projection.

## TDD evidence

- Initial RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_contract` — 11 tests
  failed with assertions that `qa_contract.py` was missing; there was no import error.
- First GREEN attempt: 11 tests ran with one diagnostic assertion failure because a numeric
  timestamp was rejected as a generic string type instead of a timestamp violation.
- First GREEN: the same focused command passed 11 tests after the minimal diagnostic correction.
- Review RED: the expanded focused suite ran 13 tests with 4 failures proving missing enforcement
  for duplicate JSON fields, non-applicable reasons, declared evidence sizes, and disconnected
  retest chains.
- Final GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_contract` — 13 tests
  passed.
- QA regression: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest $(rg --files tests | sed -n
  's#^tests/\(test_qa_[^/]*\)\.py$#tests.\1#p' | sort | tr '\n' ' ')` — 76 tests passed on
  Python 3.9.6.
- Contract checks: Python compilation, `python3 -m json.tool` for the schema, and
  `git diff --check` all passed.

## Limitations

- This layer validates declared evidence sizes (10 MiB each and 100 MiB total). A later evidence
  inspector must re-check actual files, their aggregate size, regular-file/symlink confinement,
  hashes, credential patterns, sanitization, and the 20-megapixel image limit.
- No evidence command was executed and no plugin used as a reference, ledger, review artifact,
  dependency, personal configuration, external state, publication, push, or merge was changed.
