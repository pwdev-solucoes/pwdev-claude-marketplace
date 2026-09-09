# Task 03 — brief

Plan: .planning/power/features/sdd-composy-f02-init-map/plan.md
Generated: 2026-09-08T18:48:59Z

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

## Task 03 — Safe initialization helper
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_init.py`, `tests/test_sdd_composy_runtime.py`
Interfaces:
  Consumes: template root and F01 schemas
  Produces: `inspect`, `plan`, `apply`, and `verify` commands plus OKF v0.2 bundle initialization
Steps:
- [ ] Add failing temporary-repository tests for clean init, OKF actor/index creation, idempotence, file conflict, directory conflict, and unsafe symlink refusal.
- [ ] Run the focused test and observe expected failures.
- [ ] Implement repository-bound safe-path checks, atomic writes, template rendering, and `.claude -> .agents` creation.
- [ ] Ensure `apply` requires the exact plan token emitted by `plan` when conflicts exist.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
