# Task 06 — brief

Plan: .planning/power/features/sdd-composy-f05-quality/plan.md
Generated: 2026-09-09T09:32:06Z

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

## Task 06 — Verification adapter and lifecycle integration
Complexity: high
Files: `plugins/sdd-composy/commands/verify.md`, `plugins/sdd-composy/scripts/sdd_tasks.py`, `tests/test_sdd_composy_quality.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: verified QA/review/verdict artifacts
  Produces: guarded quality-state transitions and Claude verification adapter
Steps:
- [ ] Add failing end-to-end state tests from `running` through `complete` and each rejection path.
- [ ] Run both quality and task test modules.
- [ ] Connect artifact evidence predicates to task transition guards and add the thin adapter.
- [ ] Re-run both test modules.
- [ ] Commit only when explicitly authorized.
