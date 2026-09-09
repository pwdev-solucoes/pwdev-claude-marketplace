# Task 08 — brief

Plan: .planning/power/features/sdd-composy-f05-quality/plan.md
Generated: 2026-09-09T09:43:13Z

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

## Task 08 — Evidence skill and adapters
Complexity: high
Files: `plugins/sdd-composy/skills/sdd-evidence/SKILL.md`, `plugins/sdd-composy/skills/sdd-evidence/agents/openai.yaml`, `plugins/sdd-composy/commands/evidence.md`, `plugins/sdd-composy/scripts/sdd_tasks.py`, `tests/test_sdd_composy_quality.py`
Interfaces:
  Consumes: `sdd_evidence.py build|verify|export`
  Produces: portable `$sdd-evidence`, `/sdd-composy:evidence`, and guarded `evidence_required -> review_required` transition
Steps:
- [ ] Add failing discovery, route, optional-PDF, existing-evidence rebuild, and lifecycle transition tests.
- [ ] Run structural, quality, and task tests.
- [ ] Implement skill, metadata, thin adapter, and task-engine evidence guard.
- [ ] Re-run structural, quality, and task tests.
- [ ] Commit only when explicitly authorized.
