# Task 07 — brief

Plan: .planning/power/features/sdd-composy-f05-quality/plan.md
Generated: 2026-09-09T09:38:39Z

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

## Task 07 — Evidence manifest and renderer
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_evidence.py`, `plugins/sdd-composy/templates/evidence-report.md`, `plugins/sdd-composy/references/evidence.md`, `tests/test_sdd_composy_quality.py`
Interfaces:
  Consumes: `evidence_required` task, approved CA/test results, screenshots/attachments, and F01 evidence schema
  Produces: validated `manifest.json`, escaped `evidence-report.html`, optional verified PDF, and artifact hashes
Steps:
- [ ] Add failing tests for path traversal, symlinks, unknown enums, result/type separation, missing files, HTML injection, hashes, and unloaded PDF images.
- [ ] Run the quality test and observe failures.
- [ ] Implement `build`, `verify`, and `export` with fail-closed validation and no stack-specific commands.
- [ ] Re-run the quality test.
- [ ] Commit only when explicitly authorized.
