# Task 02 — brief

Plan: .planning/power/features/sdd-composy-f06-observability/plan.md
Generated: 2026-09-09T10:01:32Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Never edit `trace.json` directly or repair an invalid audit trail automatically.
- Semantic events are recorded only after the represented action succeeds.
- Never record prompts, output dumps, environment variables, secrets, models, or private paths.
- Status is strictly read-only.
- Quick touches at most 5 implementation files and excludes architecture, migrations, destructive work, and unknown verification.
- Quick contracts and reports conform to OKF v0.2 and remain linked from the bundle index.

## Task 02 — Trace projection
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_trace.py`, `tests/test_sdd_composy_observability.py`
Interfaces:
  Consumes: valid PRD/stories/TechSpec/tasks/evidence identifiers and valid semantic events
  Produces: deterministic `build`, `query`, and `verify-projection` for `trace.json`, including evidence artifact hashes
Steps:
- [ ] Add failing graph tests for RF-US-SC-CA-task-test-evidence-manifest-artifact-hash-verdict links, dangling IDs, duplicate IDs, and deterministic rebuild.
- [ ] Run the focused test and observe failure.
- [ ] Implement graph assembly, source-event count binding, atomic publication, and queries.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
