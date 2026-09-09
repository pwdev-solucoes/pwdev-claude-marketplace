# Task 02 — brief

Plan: .planning/power/features/sdd-composy-f01-foundation/plan.md
Generated: 2026-09-08T15:40:11Z

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

## Task 02 — Workflow and artifact contracts
Complexity: medium
Files: `plugins/sdd-composy/references/workflow.md`, `plugins/sdd-composy/references/artifacts.md`, `plugins/sdd-composy/references/states.md`, `plugins/sdd-composy/references/safety.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: approved lifecycle and dual-root decision
  Produces: canonical lifecycle, artifact ownership, state transitions, and safety contract
Steps:
- [ ] Add failing tests for required lifecycle, roots, gates, and secret prohibitions.
- [ ] Run the focused suite and observe contract failures.
- [ ] Write the four shared references with no runtime-specific orchestration.
- [ ] Re-run the focused suite.
- [ ] Commit only when explicitly authorized.
