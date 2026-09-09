# Task 05 — brief

Plan: .planning/power/features/sdd-composy-f05-quality/plan.md
Generated: 2026-09-09T09:27:11Z

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

## Task 05 — Verification contract
Complexity: high
Files: `plugins/sdd-composy/templates/verdict.md`, `plugins/sdd-composy/references/verification.md`, `plugins/sdd-composy/skills/sdd-verify/SKILL.md`, `plugins/sdd-composy/skills/sdd-verify/agents/openai.yaml`, `tests/test_sdd_composy_quality.py`
Interfaces:
  Consumes: `verify_required` task and claimed truths from prior artifacts
  Produces: independently reproduced truth table and `complete` or `rejected` transition request
Steps:
- [ ] Add failing tests for fresh commands, truth refutation, stale evidence rejection, environment failure classification, and verdict values.
- [ ] Run the focused test and observe failure.
- [ ] Implement template, reference, skill, and metadata.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
