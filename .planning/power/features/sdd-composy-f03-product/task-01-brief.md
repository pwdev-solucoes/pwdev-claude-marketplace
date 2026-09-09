# Task 01 — brief

Plan: .planning/power/features/sdd-composy-f03-product/plan.md
Generated: 2026-09-08T23:30:55Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Human contracts remain under `tasks/prd-<slug>/`.
- Existence does not imply approval; every gate is human-recorded.
- Product documents do not make architecture decisions.
- Stories are required for user-facing behavior and externally consumed APIs; internal work records `NOT_APPLICABLE` with justification.
- Trace IDs are `RF-*`, `US-*`, `SC-*`, `CA-*`, `TU-*`, `TI-*`, and `E2E-*`.
- PRD, stories, and TechSpec are OKF v0.2 concepts with upstream `sources`, generated actor/timestamp, lifecycle status, and human `verified` gate events.

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
