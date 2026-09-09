# Task 08 — brief

Plan: .planning/power/features/sdd-composy-f08-fleet/plan.md
Generated: 2026-09-09T13:07:44Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Fleet accepts only ready tasks with complete dependencies, explicit acceptance criteria, known verification commands, and no confirmed path overlap.
- Never merge fleet branches automatically.
- Preserve recoverable branches and worktrees after failure.
- Runtime-specific provider command vectors are built only in their dedicated adapters.
- cmux is a presentation adapter and must not own process lifecycle truth.
- cmux operations are restricted to the workspace created by this fleet.
- Never read or adopt an existing `.env.fleet`.

## Task 08 — Fleet skill and final integration
Complexity: high
Files: `plugins/sdd-composy/skills/sdd-fleet/SKILL.md`, `plugins/sdd-composy/skills/sdd-fleet/agents/openai.yaml`, `plugins/sdd-composy/commands/fleet.md`, `tests/test_sdd_composy.py`, `tests/test_marketplace_readmes.py`
Interfaces:
  Consumes: launch/status/teardown routes and all completed SDD contracts
  Produces: portable `$sdd-fleet`, `/sdd-composy:fleet`, registered 17-skill plugin, and final validation evidence
Steps:
- [ ] Add failing route, authorization, adapter-order, full-catalogue, README, and marketplace coverage tests.
- [ ] Run `python3 -m unittest tests.test_sdd_composy tests.test_marketplace_readmes`.
- [ ] Implement skill, metadata, adapter, and final documentation references.
- [ ] Run all `tests.test_sdd_composy*` modules explicitly, the OKF v0.2 linter fixtures, marketplace tests, and plugin validators.
- [ ] Inspect the full plugin diff for secrets, placeholders, runtime coupling, and scope drift.
- [ ] Commit only when explicitly authorized.
