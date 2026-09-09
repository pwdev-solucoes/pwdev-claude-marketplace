# Task 01 — brief

Plan: .planning/power/features/sdd-composy-f06-observability/plan.md
Generated: 2026-09-09T09:57:53Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Never edit `trace.json` directly or repair an invalid audit trail automatically.
- Semantic events are recorded only after the represented action succeeds.
- Never record prompts, output dumps, environment variables, secrets, models, or private paths.
- Status is strictly read-only.
- Quick touches at most 5 implementation files and excludes architecture, migrations, destructive work, and unknown verification.
- Quick contracts and reports conform to OKF v0.2 and remain linked from the bundle index.

## Task 01 — Append-only semantic events
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_trace.py`, `plugins/sdd-composy/references/trace.md`, `tests/test_sdd_composy_observability.py`
Interfaces:
  Consumes: validated semantic event arguments
  Produces: `record`, `events`, `summary`, and `verify` over `trace/events.jsonl`
Steps:
- [ ] Add failing tests for disabled no-op, safe append, invalid JSONL, prohibited keys, unsafe targets, and append preservation.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_observability` and observe failure.
- [ ] Implement safe directory traversal, mode-restricted append, event validation, and queries.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
