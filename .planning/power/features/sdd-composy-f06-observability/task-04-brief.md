# Task 04 — brief

Plan: .planning/power/features/sdd-composy-f06-observability/plan.md
Generated: 2026-09-09T10:09:15Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Never edit `trace.json` directly or repair an invalid audit trail automatically.
- Semantic events are recorded only after the represented action succeeds.
- Never record prompts, output dumps, environment variables, secrets, models, or private paths.
- Status is strictly read-only.
- Quick touches at most 5 implementation files and excludes architecture, migrations, destructive work, and unknown verification.
- Quick contracts and reports conform to OKF v0.2 and remain linked from the bundle index.

## Task 04 — Consolidated status helper
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_status.py`, `plugins/sdd-composy/references/status.md`, `tests/test_sdd_composy_observability.py`
Interfaces:
  Consumes: config, global state, task files, trace integrity, loop records, and fleet records
  Produces: read-only text/JSON snapshot with exact next valid action
Steps:
- [ ] Add failing tests for uninitialized, active, blocked, divergent, looping, fleet, malformed, and no-write behavior.
- [ ] Run the focused test and observe failure.
- [ ] Implement aggregation with source confidence and actionable mismatch reporting.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
