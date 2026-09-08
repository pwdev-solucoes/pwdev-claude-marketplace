# Task 02 — brief

Plan: .planning/power/features/sdd-composy-f02-init-map/plan.md
Generated: 2026-09-08T18:35:58Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- `AGENTS.md` is canonical; `CLAUDE.md` points readers to it.
- Create `.claude -> .agents` only after compatibility and collision preflight.
- Never overwrite existing governance files, symlinks, `.agents`, or `.claude` paths.
- Never read `.env`, credentials, tokens, private keys, certificates, or existing fleet environment files.
- A re-run is idempotent.
- The map records the source commit and is observation, never architectural intent.
- Initialization records an OKF actor ID and creates the `tasks/index.md` bundle root without overwriting an existing index.

## Task 02 — Rule templates
Complexity: medium
Files: `plugins/sdd-composy/templates/rules/00-sdd-composy.md`, `plugins/sdd-composy/templates/rules/architecture.md`, `plugins/sdd-composy/templates/rules/testing.md`, `plugins/sdd-composy/templates/rules/workflow.md`, `tests/test_sdd_composy_runtime.py`
Interfaces:
  Consumes: governance contract from Task 01
  Produces: segmented `.agents/rules` template set
Steps:
- [ ] Add failing rule-discovery and responsibility tests.
- [ ] Run the focused test and observe missing rules.
- [ ] Implement non-duplicative rule templates linked by `AGENTS.md`.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
