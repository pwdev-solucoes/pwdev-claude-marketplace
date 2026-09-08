# Task 01 — brief

Plan: .planning/power/features/sdd-composy-f01-foundation/plan.md
Generated: 2026-09-08T15:27:08Z

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

## Task 01 — Scaffold and manifests
Complexity: low
Files: `plugins/sdd-composy/.claude-plugin/plugin.json`, `plugins/sdd-composy/.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: plugin identifier `sdd-composy`
  Produces: installable Claude/Codex manifests and marketplace registration
Steps:
- [ ] Add failing manifest and marketplace discovery tests.
- [ ] Run `python3 -m unittest tests.test_sdd_composy` and confirm the missing plugin failure.
- [ ] Scaffold both manifests and append marketplace entries without altering existing entries.
- [ ] Run the focused test and confirm it passes.
- [ ] Commit only when explicitly authorized.
