# Task 03 — brief

Plan: .planning/power/features/sdd-composy-f09-language/plan.md
Generated: 2026-09-09T13:38:28Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Never generate artifacts before language is resolved.
- Never translate machine keys, IDs, schemas, filenames, or command names.
- Invalid language values fail without mutation.
- All writes remain atomic and path-confined.

## Task 03 — Artifact routing and final validation
Complexity: medium
Files: `plugins/sdd-composy/references/workflow.md`, `plugins/sdd-composy/README.md`, `plugins/sdd-composy/README.pt-BR.md`, `tests/test_sdd_composy.py`, `tests/test_sdd_composy_language.py`
Interfaces:
  Consumes: resolved language contract.
  Produces: documented PT-BR/EN-US artifact behavior and compatibility tests.
Steps:
- [ ] Add failing route/documentation tests.
- [ ] Implement shared routing guidance and bilingual docs.
- [ ] Run all language, structural, and full SDD Composy tests.
- [ ] Record final report.
