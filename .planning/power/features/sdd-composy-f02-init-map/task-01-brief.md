# Task 01 — brief

Plan: .planning/power/features/sdd-composy-f02-init-map/plan.md
Generated: 2026-09-08T18:29:34Z

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

## Task 01 — Governance root templates
Complexity: medium
Files: `plugins/sdd-composy/templates/AGENTS.md`, `plugins/sdd-composy/templates/CLAUDE.md`, `tests/test_sdd_composy_runtime.py`
Interfaces:
  Consumes: F01 workflow and artifact contracts
  Produces: renderable canonical governance templates
Steps:
- [ ] Add failing tests for required codebase, commands, workflow, gates, artifact, and safety sections.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_runtime` and observe failure.
- [ ] Write templates with explicit render variables and no unresolved scaffold placeholders in installed output.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
