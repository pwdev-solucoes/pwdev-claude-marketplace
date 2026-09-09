# Task 05 — brief

Plan: .planning/power/features/sdd-composy-f03-product/plan.md
Generated: 2026-09-09T00:12:34Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Human contracts remain under `tasks/prd-<slug>/`.
- Existence does not imply approval; every gate is human-recorded.
- Product documents do not make architecture decisions.
- Stories are required for user-facing behavior and externally consumed APIs; internal work records `NOT_APPLICABLE` with justification.
- Trace IDs are `RF-*`, `US-*`, `SC-*`, `CA-*`, `TU-*`, `TI-*`, and `E2E-*`.
- PRD, stories, and TechSpec are OKF v0.2 concepts with upstream `sources`, generated actor/timestamp, lifecycle status, and human `verified` gate events.

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
