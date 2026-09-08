# Task 05 — brief

Plan: .planning/power/features/sdd-composy-f02-init-map/plan.md
Generated: 2026-09-08T19:15:18Z

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

## Task 05 — Codebase map helper
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_map.py`, `plugins/sdd-composy/references/mapping.md`, `tests/test_sdd_composy_runtime.py`
Interfaces:
  Consumes: repository root and governance without secret files
  Produces: OKF v0.2 context concepts and `codebase.json` with commit, commands, modules, boundaries, and confidence
Steps:
- [ ] Add failing fixture tests for stack detection, manifest-derived commands, domain evidence, staleness, and secret exclusion.
- [ ] Run the focused test and observe failure.
- [ ] Implement adaptive read-only inventory and deterministic serialized output.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
