# Task 06 — brief

Plan: .planning/power/features/sdd-composy-f01-foundation/plan.md
Generated: 2026-09-08T16:27:03Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Plugin identifier and directory name are exactly `sdd-composy`.
- Support Claude Code and Codex from the same portable contracts.
- The plugin has no runtime dependency on `pwdev-flow` or `pwdev-feat`.
- Human contracts remain under `tasks/prd-<slug>/`.
- Operational state remains under `.planning/sdd-composy/`.
- Never read `.env`, credentials, tokens, private keys, certificates, or existing fleet environment files.
- Preserve unknown JSON fields during supported updates.
- Generated project Markdown targets OKF v0.2; `type` is required and unknown extension fields remain permitted.

## Task 06 — Structural validation
Complexity: medium
Files: `tests/test_sdd_composy.py`, `tests/test_marketplace_readmes.py`
Interfaces:
  Consumes: all F01 files
  Produces: green structural and marketplace validation commands for later phases
Steps:
- [ ] Extend tests to reject placeholders, broken relative links, divergent manifest versions, and unregistered skills.
- [ ] Run `python3 -m unittest tests.test_sdd_composy tests.test_marketplace_readmes`.
- [ ] Fix only F01 contract defects exposed by the tests.
- [ ] Re-run both modules and read the complete result.
- [ ] Commit only when explicitly authorized.
