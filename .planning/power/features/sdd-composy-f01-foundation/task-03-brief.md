# Task 03 — brief

Plan: .planning/power/features/sdd-composy-f01-foundation/plan.md
Generated: 2026-09-08T15:53:48Z

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

## Task 03 — Runtime contract
Complexity: medium
Files: `plugins/sdd-composy/references/runtime.md`, `plugins/sdd-composy/README.md`, `plugins/sdd-composy/README.pt-BR.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: shared plugin layout from Task 01
  Produces: exact discovery and adapter rules for Claude Code and Codex
Steps:
- [ ] Add failing portability and documentation tests.
- [ ] Run the focused suite and observe failure.
- [ ] Document shared-core discovery and thin Claude adapter behavior in both languages.
- [ ] Re-run the focused suite.
- [ ] Commit only when explicitly authorized.
