# Task 07 — brief

Plan: .planning/power/features/sdd-composy-f06-observability/plan.md
Generated: 2026-09-09T10:20:42Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Never edit `trace.json` directly or repair an invalid audit trail automatically.
- Semantic events are recorded only after the represented action succeeds.
- Never record prompts, output dumps, environment variables, secrets, models, or private paths.
- Status is strictly read-only.
- Quick touches at most 5 implementation files and excludes architecture, migrations, destructive work, and unknown verification.
- Quick contracts and reports conform to OKF v0.2 and remain linked from the bundle index.

## Task 07 — Quick adapter and integrated validation
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-quick/agents/openai.yaml`, `plugins/sdd-composy/commands/quick.md`, `tests/test_sdd_composy.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: `$sdd-quick` contract from Task 06
  Produces: Claude adapter and verified quick-to-full escalation boundary
Steps:
- [ ] Add failing discovery, adapter, and escalation integration tests.
- [ ] Run structural and task tests.
- [ ] Implement metadata and thin adapter, then connect any missing task transition.
- [ ] Re-run structural, task, and observability tests.
- [ ] Commit only when explicitly authorized.
