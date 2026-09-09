# Task 04 — brief

Plan: .planning/power/features/sdd-composy-f01-foundation/plan.md
Generated: 2026-09-08T16:01:13Z

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

## Task 04 — Core schemas
Complexity: high
Files: `plugins/sdd-composy/schemas/config.schema.json`, `plugins/sdd-composy/schemas/state.schema.json`, `plugins/sdd-composy/schemas/tasks.schema.json`, `plugins/sdd-composy/schemas/trace.schema.json`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: state and artifact contracts from Task 02
  Produces: version-1 validation schemas for configuration, global state, task state, and trace projection
Steps:
- [ ] Add failing schema-shape and valid/invalid fixture tests.
- [ ] Run the focused suite and confirm missing-schema failures.
- [ ] Implement strict required fields, enums, identifier patterns, and extension-safe objects.
- [ ] Re-run the focused suite.
- [ ] Commit only when explicitly authorized.
