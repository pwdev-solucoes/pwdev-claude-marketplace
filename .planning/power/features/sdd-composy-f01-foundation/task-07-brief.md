# Task 07 — brief

Plan: .planning/power/features/sdd-composy-f01-foundation/plan.md
Generated: 2026-09-08T16:48:00Z

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

## Task 07 — OKF v0.2 contract and linter
Complexity: high
Files: `plugins/sdd-composy/references/okf.md`, `plugins/sdd-composy/scripts/sdd_okf.py`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: an SDD project artifact root and configured actor ID
  Produces: `lint`, `index`, and frontmatter validation for OKF v0.2 project documents
Steps:
- [ ] Add failing tests for required `type`, permissive extensions, generated/verified actors, ISO timestamps, sources, reserved index/log behavior, and broken-link reporting.
- [ ] Run `python3 -m unittest tests.test_sdd_composy` and observe failures.
- [ ] Implement OKF parsing and linting without requiring optional fields for base conformance.
- [ ] Add root-index generation with `okf_version: "0.2"` and progressive-disclosure entries.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
