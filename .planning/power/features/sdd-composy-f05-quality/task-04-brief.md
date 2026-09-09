# Task 04 — brief

Plan: .planning/power/features/sdd-composy-f05-quality/plan.md
Generated: 2026-09-09T09:23:03Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints
- Never let execution change approved requirements, stories, architecture, or scope.
- No production behavior change without a failing test first.
- No defect correction without root-cause investigation.
- No completion claim without fresh verification evidence.
- Services started by a run are recorded and cleaned without touching user-owned processes.
- QA and review blockers prevent forward task transitions.
- Evidence manifests use confined relative paths, SHA-256 digests, known enums, and sanitized content.
- PDF export is optional unless requested; a requested export fails when expected images do not load.
- QA, evidence, review, and verdict Markdown reports conform to OKF v0.2 and record verification actors separately from generation actors.

## Task 04 — Review contract
Complexity: high
Files: `plugins/sdd-composy/templates/codereview.md`, `plugins/sdd-composy/skills/sdd-review/SKILL.md`, `plugins/sdd-composy/skills/sdd-review/agents/openai.yaml`, `plugins/sdd-composy/commands/review.md`, `tests/test_sdd_composy_quality.py`
Interfaces:
  Consumes: explicit diff scope, approved contracts, task evidence, and project rules
  Produces: `codereview.md` and transition to `verify_required` or `rejected`
Steps:
- [ ] Add failing tests for base/target scope, severity, rule citations, commands, skill conformity, blocker status, and no-silent-fix behavior.
- [ ] Run the focused test and observe failure.
- [ ] Implement review template, skill, metadata, and adapter.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
