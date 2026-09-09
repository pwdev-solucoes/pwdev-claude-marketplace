# Task 02 — brief

Plan: .planning/power/features/sdd-composy-f03-product/plan.md
Generated: 2026-09-08T23:39:10Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Human contracts remain under `tasks/prd-<slug>/`.
- Existence does not imply approval; every gate is human-recorded.
- Product documents do not make architecture decisions.
- Stories are required for user-facing behavior and externally consumed APIs; internal work records `NOT_APPLICABLE` with justification.
- Trace IDs are `RF-*`, `US-*`, `SC-*`, `CA-*`, `TU-*`, `TI-*`, and `E2E-*`.
- PRD, stories, and TechSpec are OKF v0.2 concepts with upstream `sources`, generated actor/timestamp, lifecycle status, and human `verified` gate events.

## Task 02 — PRD skill and adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-prd/SKILL.md`, `plugins/sdd-composy/skills/sdd-prd/agents/openai.yaml`, `plugins/sdd-composy/commands/prd.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: Task 01 product contract
  Produces: portable `$sdd-prd` and `/sdd-composy:prd`
Steps:
- [ ] Add failing routing and gate tests.
- [ ] Run the structural test.
- [ ] Implement the skill, metadata, and adapter without runtime-specific tool names.
- [ ] Re-run structural and product tests.
- [ ] Commit only when explicitly authorized.
