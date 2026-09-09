# Task 01 — brief

Plan: .planning/power/features/sdd-composy-f05-quality/plan.md
Generated: 2026-09-09T09:00:01Z

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

## Task 01 — Execution contract
Complexity: high
Files: `plugins/sdd-composy/references/execution.md`, `plugins/sdd-composy/skills/sdd-execute/SKILL.md`, `plugins/sdd-composy/skills/sdd-execute/agents/openai.yaml`, `plugins/sdd-composy/commands/execute.md`, `tests/test_sdd_composy_quality.py`
Interfaces:
  Consumes: one `ready` task, its Markdown contract, codebase context, and real verification commands
  Produces: implementation evidence and transition to `qa_required`, `blocked`, or `rejected`
Steps:
- [ ] Add failing tests for dependency preflight, TDD, allowed paths, command evidence, environment ownership, and transition outcomes.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_quality` and observe failure.
- [ ] Implement the execution reference, skill, metadata, and thin adapter.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
