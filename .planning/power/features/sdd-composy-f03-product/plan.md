# SDD Composy F03 Product Contracts — Plan
Status: APPROVED
Spec: .planning/power/features/sdd-composy/spec.md
Updated: 2026-09-08

For agentic workers: execute this with pwdev-power:power-execute.

## Goal
Adapt PRD and TechSpec creation and add a distinct user-story gate with stable cross-document identifiers.

## Architecture
Each producer reads approved upstream artifacts and writes one human contract. Stable IDs are validated by tests and later imported by F04.

## Tech Stack
Markdown skills, templates, thin Claude commands, Python `unittest` contract tests.

## Global Constraints
- Human contracts remain under `tasks/prd-<slug>/`.
- Existence does not imply approval; every gate is human-recorded.
- Product documents do not make architecture decisions.
- Stories are required for user-facing behavior and externally consumed APIs; internal work records `NOT_APPLICABLE` with justification.
- Trace IDs are `RF-*`, `US-*`, `SC-*`, `CA-*`, `TU-*`, `TI-*`, and `E2E-*`.
- PRD, stories, and TechSpec are OKF v0.2 concepts with upstream `sources`, generated actor/timestamp, lifecycle status, and human `verified` gate events.

## File Structure
- `plugins/sdd-composy/templates/{prd,stories,techspec}.md`
- `plugins/sdd-composy/references/{product,stories,specification}.md`
- `plugins/sdd-composy/skills/{sdd-prd,sdd-stories,sdd-techspec}/`
- `plugins/sdd-composy/commands/{prd,stories,techspec}.md`
- `tests/test_sdd_composy_product.py`

## Task 01 — PRD contract
Complexity: medium
Files: `plugins/sdd-composy/templates/prd.md`, `plugins/sdd-composy/references/product.md`, `tests/test_sdd_composy_product.py`
Interfaces:
  Consumes: user problem and optional codebase/domain context
  Produces: `tasks/prd-<slug>/prd.md` with stable RF and CA identifiers and an explicit gate
Steps:
- [ ] Add failing tests for objectives, metrics, scope, assumptions, dependencies, open questions, RFs, CAs, and one approval field.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_product` and observe failure.
- [ ] Adapt the source PRD template and write its contract reference.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

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

## Task 04 — User-story Claude adapter
Complexity: low
Files: `plugins/sdd-composy/commands/stories.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `$sdd-stories` contract from Task 03
  Produces: `/sdd-composy:stories`
Steps:
- [ ] Add a failing thin-adapter test.
- [ ] Run the structural test.
- [ ] Write the adapter without duplicating workflow instructions.
- [ ] Re-run the structural test.
- [ ] Commit only when explicitly authorized.

## Task 05 — TechSpec contract
Complexity: high
Files: `plugins/sdd-composy/templates/techspec.md`, `plugins/sdd-composy/references/specification.md`, `tests/test_sdd_composy_product.py`
Interfaces:
  Consumes: approved PRD, approved/applicability-resolved stories, and codebase context
  Produces: `techspec.md` with components, contracts, decisions, risks, and named test cases
Steps:
- [ ] Add failing tests for upstream gates, component inventory, interfaces, data/API conditional sections, decisions, and CA-linked TU/TI/E2E cases.
- [ ] Run the product test and observe failure.
- [ ] Create a concise core template with conditional details routed through the reference.
- [ ] Re-run the product test.
- [ ] Commit only when explicitly authorized.

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
