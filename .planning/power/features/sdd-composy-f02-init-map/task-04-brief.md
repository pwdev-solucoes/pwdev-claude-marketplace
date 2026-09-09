# Task 04 — brief

Plan: .planning/power/features/sdd-composy-f02-init-map/plan.md
Generated: 2026-09-08T19:09:51Z

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

## Task 04 — Init skill and Claude adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-init/SKILL.md`, `plugins/sdd-composy/skills/sdd-init/agents/openai.yaml`, `plugins/sdd-composy/commands/init.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `sdd_init.py inspect|plan|apply|verify`
  Produces: portable `$sdd-init` and `/sdd-composy:init`
Steps:
- [ ] Add failing discovery, routing, and command-thinness tests.
- [ ] Run the structural test and observe failure.
- [ ] Write the skill, metadata, and thin command adapter.
- [ ] Re-run the structural test.
- [ ] Commit only when explicitly authorized.
