# Task 03 — brief

Plan: .planning/power/features/sdd-composy-f06-observability/plan.md
Generated: 2026-09-09T10:06:24Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Never edit `trace.json` directly or repair an invalid audit trail automatically.
- Semantic events are recorded only after the represented action succeeds.
- Never record prompts, output dumps, environment variables, secrets, models, or private paths.
- Status is strictly read-only.
- Quick touches at most 5 implementation files and excludes architecture, migrations, destructive work, and unknown verification.
- Quick contracts and reports conform to OKF v0.2 and remain linked from the bundle index.

## Task 03 — Trace skill and adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-trace/SKILL.md`, `plugins/sdd-composy/skills/sdd-trace/agents/openai.yaml`, `plugins/sdd-composy/commands/trace.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `sdd_trace.py record|events|summary|verify|build|query|verify-projection`
  Produces: portable `$sdd-trace` and `/sdd-composy:trace`
Steps:
- [ ] Add failing route and safety tests.
- [ ] Run the structural test.
- [ ] Implement skill, metadata, and adapter.
- [ ] Run structural and observability tests.
- [ ] Commit only when explicitly authorized.
