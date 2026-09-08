# Task 05 — brief

Plan: .planning/power/features/sdd-composy-f01-foundation/plan.md
Generated: 2026-09-08T16:13:37Z

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

## Task 05 — Autonomous, fleet, and evidence schemas
Complexity: high
Files: `plugins/sdd-composy/schemas/loop.schema.json`, `plugins/sdd-composy/schemas/fleet-member.schema.json`, `plugins/sdd-composy/schemas/fleet-result.schema.json`, `plugins/sdd-composy/schemas/evidence-manifest.schema.json`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: lifecycle states from Task 02
  Produces: loop/fleet operational contracts and a criterion-linked evidence manifest contract
Steps:
- [ ] Add failing tests for the 3-iteration default, terminal states, runtime/UI enums, evidence result/type separation, confined paths, and hashes.
- [ ] Run the focused suite and observe failures.
- [ ] Implement the three schemas and cross-field invariants testable by fixtures.
- [ ] Re-run the focused suite.
- [ ] Commit only when explicitly authorized.
