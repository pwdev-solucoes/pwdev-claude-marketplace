# Task 03 — brief

Plan: .planning/power/features/sdd-composy-f03-product/plan.md
Generated: 2026-09-08T23:45:52Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Human contracts remain under `tasks/prd-<slug>/`.
- Existence does not imply approval; every gate is human-recorded.
- Product documents do not make architecture decisions.
- Stories are required for user-facing behavior and externally consumed APIs; internal work records `NOT_APPLICABLE` with justification.
- Trace IDs are `RF-*`, `US-*`, `SC-*`, `CA-*`, `TU-*`, `TI-*`, and `E2E-*`.
- PRD, stories, and TechSpec are OKF v0.2 concepts with upstream `sources`, generated actor/timestamp, lifecycle status, and human `verified` gate events.

## Task 03 — User-story contract and skill
Complexity: medium
Files: `plugins/sdd-composy/templates/stories.md`, `plugins/sdd-composy/references/stories.md`, `plugins/sdd-composy/skills/sdd-stories/SKILL.md`, `plugins/sdd-composy/skills/sdd-stories/agents/openai.yaml`, `tests/test_sdd_composy_product.py`
Interfaces:
  Consumes: approved `prd.md`, `domain.md`, optional `project.md`
  Produces: approved or justified `NOT_APPLICABLE` `stories.md` with US and SC identifiers
Steps:
- [ ] Add failing tests for actors, journeys, US/SC uniqueness, RF/CA links, dependencies, edge cases, and applicability gate.
- [ ] Run the product test and observe failure.
- [ ] Implement template, reference, skill, and metadata.
- [ ] Re-run the product test.
- [ ] Commit only when explicitly authorized.
