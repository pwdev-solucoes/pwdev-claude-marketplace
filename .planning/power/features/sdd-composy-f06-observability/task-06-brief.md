# Task 06 — brief

Plan: .planning/power/features/sdd-composy-f06-observability/plan.md
Generated: 2026-09-09T10:17:30Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Never edit `trace.json` directly or repair an invalid audit trail automatically.
- Semantic events are recorded only after the represented action succeeds.
- Never record prompts, output dumps, environment variables, secrets, models, or private paths.
- Status is strictly read-only.
- Quick touches at most 5 implementation files and excludes architecture, migrations, destructive work, and unknown verification.
- Quick contracts and reports conform to OKF v0.2 and remain linked from the bundle index.

## Task 06 — Quick path
Complexity: high
Files: `plugins/sdd-composy/templates/quick-contract.md`, `plugins/sdd-composy/templates/quick-report.md`, `plugins/sdd-composy/references/quick.md`, `plugins/sdd-composy/skills/sdd-quick/SKILL.md`, `tests/test_sdd_composy_observability.py`
Interfaces:
  Consumes: bounded objective, acceptance criteria, allowed files, and known verification commands
  Produces: Q-ID task record, contract, report, trace events, and verified verdict
Steps:
- [ ] Add failing tests for the five-file gate, forbidden categories, TDD, escalation, normal task registration, and evidence.
- [ ] Run the focused test and observe failure.
- [ ] Implement templates, reference, skill, and task/trace integration contract.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
