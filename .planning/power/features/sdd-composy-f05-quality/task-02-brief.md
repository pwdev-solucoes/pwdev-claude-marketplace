# Task 02 — brief

Plan: .planning/power/features/sdd-composy-f05-quality/plan.md
Generated: 2026-09-09T09:08:16Z

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

## Task 02 — QA contract
Complexity: high
Files: `plugins/sdd-composy/templates/qa.md`, `plugins/sdd-composy/references/quality.md`, `plugins/sdd-composy/skills/sdd-qa/SKILL.md`, `plugins/sdd-composy/skills/sdd-qa/agents/openai.yaml`, `tests/test_sdd_composy_quality.py`
Interfaces:
  Consumes: `qa_required` task, CA/SC/test mappings, and browser capability when applicable
  Produces: `qa.md`, regression evidence, and transition to `evidence_required` or `rejected`
Steps:
- [ ] Add failing tests for CA coverage, unit/integration/E2E results, accessibility, responsiveness, environment, evidence inventory, and blocker semantics.
- [ ] Run the focused test and observe failure.
- [ ] Implement QA template, shared quality reference, skill, and metadata.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
