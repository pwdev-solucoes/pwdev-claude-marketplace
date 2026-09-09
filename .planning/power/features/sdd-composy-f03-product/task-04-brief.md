# Task 04 — brief

Plan: .planning/power/features/sdd-composy-f03-product/plan.md
Generated: 2026-09-09T00:07:54Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Human contracts remain under `tasks/prd-<slug>/`.
- Existence does not imply approval; every gate is human-recorded.
- Product documents do not make architecture decisions.
- Stories are required for user-facing behavior and externally consumed APIs; internal work records `NOT_APPLICABLE` with justification.
- Trace IDs are `RF-*`, `US-*`, `SC-*`, `CA-*`, `TU-*`, `TI-*`, and `E2E-*`.
- PRD, stories, and TechSpec are OKF v0.2 concepts with upstream `sources`, generated actor/timestamp, lifecycle status, and human `verified` gate events.

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
