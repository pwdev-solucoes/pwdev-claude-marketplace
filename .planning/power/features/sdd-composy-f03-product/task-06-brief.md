# Task 06 — brief

Plan: .planning/power/features/sdd-composy-f03-product/plan.md
Generated: 2026-09-09T00:19:41Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Human contracts remain under `tasks/prd-<slug>/`.
- Existence does not imply approval; every gate is human-recorded.
- Product documents do not make architecture decisions.
- Stories are required for user-facing behavior and externally consumed APIs; internal work records `NOT_APPLICABLE` with justification.
- Trace IDs are `RF-*`, `US-*`, `SC-*`, `CA-*`, `TU-*`, `TI-*`, and `E2E-*`.
- PRD, stories, and TechSpec are OKF v0.2 concepts with upstream `sources`, generated actor/timestamp, lifecycle status, and human `verified` gate events.

## Task 06 — TechSpec skill and adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-techspec/SKILL.md`, `plugins/sdd-composy/skills/sdd-techspec/agents/openai.yaml`, `plugins/sdd-composy/commands/techspec.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: Task 05 specification contract
  Produces: portable `$sdd-techspec` and `/sdd-composy:techspec`
Steps:
- [ ] Add failing routing, upstream-gate, and progressive-disclosure tests.
- [ ] Run the structural test.
- [ ] Implement the skill, metadata, and adapter.
- [ ] Run structural and product tests.
- [ ] Commit only when explicitly authorized.
