# Task 03 — implementation report

Status: DONE_WITH_CONCERNS

## Delivered

- Added `references/runtime.md` as the exact portable boundary: both hosts consume `skills/`, `references/`, `scripts/`, `templates/`, and `schemas/`; Claude uses thin `commands/<name>.md` adapters; Codex uses native discovery through `"skills": "./skills/"`.
- Defined the adapter prohibition against duplicating workflow, gate, artifact, schema, safety, and orchestration semantics.
- Defined cross-runtime resumption over `tasks/prd-<slug>/` and `.planning/sdd-composy/`, and explicit runtime independence from `pwdev-flow` and `pwdev-feat`.
- Added English and PT-BR plugin READMEs with matching invocation, artifact, OKF v0.2, portability, and safety claims.
- Added focused regression tests for shared-core discovery, thin adapters, independence, and bilingual documentation.

## Verification

Red phase:

```text
python3 -m unittest tests.test_sdd_composy
Ran 9 tests — FAILED (errors=2)
```

The new tests failed because `references/runtime.md` and the bilingual plugin READMEs did not exist.

Green phase:

```text
python3 -m unittest tests.test_sdd_composy
Ran 9 tests — OK
```

Combined baseline check:

```text
python3 -m unittest tests.test_sdd_composy tests.test_marketplace_readmes
Ran 17 tests — FAILED (failures=5)
```

All five failures are the ruled expected root-marketplace README coverage gaps for `sdd-composy` (section link, section, table row, install command, and inventory). The root READMEs are outside Task 03's file list and were not modified. No `pwdev-power` counts, schemas, or marketplace entries were changed.

## Scope

Only Task 03 implementation files, its tests, brief, and this report are intended for the task commit. Pre-existing review diff files remain untracked and untouched.
