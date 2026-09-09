# Task 03 — brief

Plan: .planning/power/features/sdd-composy-f05-quality/plan.md
Generated: 2026-09-09T09:20:50Z

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

## Task 03 — QA Claude adapter
Complexity: low
Files: `plugins/sdd-composy/commands/qa.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `$sdd-qa` contract from Task 02
  Produces: `/sdd-composy:qa`
Steps:
- [ ] Add a failing thin-adapter test.
- [ ] Run the structural test.
- [ ] Implement the adapter without duplicated QA workflow.
- [ ] Re-run structural and quality tests.
- [ ] Commit only when explicitly authorized.
