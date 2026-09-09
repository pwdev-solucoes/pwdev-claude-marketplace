# Task 01 — brief

Plan: .planning/power/features/sdd-composy-f09-language/plan.md
Generated: 2026-09-09T13:31:03Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Never generate artifacts before language is resolved.
- Never translate machine keys, IDs, schemas, filenames, or command names.
- Invalid language values fail without mutation.
- All writes remain atomic and path-confined.

## Task 01 — Language resolver
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_language.py`, `plugins/sdd-composy/references/language.md`, `tests/test_sdd_composy_language.py`
Interfaces:
  Consumes: repository root and optional explicit `pt-BR|en-US` value.
  Produces: persisted preference, init-only choices, or `{status: not_initialized, next_action: run_init}` for consumers.
Steps:
- [ ] Add failing tests for init-only missing choice, valid, invalid, persisted, override, atomicity, downstream no-prompt, and not-initialized response.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_language` and observe failure.
- [ ] Implement confined atomic resolver.
- [ ] Re-run the focused test.
- [ ] Record report.
