# Task 06 — brief

Plan: .planning/power/features/sdd-composy-f02-init-map/plan.md
Generated: 2026-09-08T19:32:43Z

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

## Task 06 — Map skill and Claude adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-map/SKILL.md`, `plugins/sdd-composy/skills/sdd-map/agents/openai.yaml`, `plugins/sdd-composy/commands/map.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `sdd_map.py` output contract
  Produces: portable `$sdd-map` and `/sdd-composy:map`
Steps:
- [ ] Add failing tests for read-only scope, output paths, staleness, and downstream routing.
- [ ] Run the structural test and observe failure.
- [ ] Implement skill, metadata, and command adapter.
- [ ] Re-run structural and runtime tests.
- [ ] Commit only when explicitly authorized.
