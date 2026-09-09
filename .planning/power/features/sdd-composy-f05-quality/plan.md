# SDD Composy F05 Execution and Quality — Plan
Status: APPROVED
Spec: .planning/power/features/sdd-composy/spec.md
Updated: 2026-09-08

For agentic workers: execute this with pwdev-power:power-execute.

## Goal
Implement the single-task delivery path and independent QA, evidence-publication, code-review, and adversarial-verification gates.

## Architecture
Skills orchestrate project-native commands and persist concise evidence. The task engine owns state transitions. QA tests, evidence publishes a dossier, review does not silently fix, and verification independently tests the claims.

## Tech Stack
Markdown skills/templates, Python task helper integration, browser-tool capability abstraction, Python `unittest` contract tests.

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

## File Structure
- `plugins/sdd-composy/skills/{sdd-execute,sdd-qa,sdd-evidence,sdd-review,sdd-verify}/`
- `plugins/sdd-composy/commands/{execute,qa,evidence,review,verify}.md`
- `plugins/sdd-composy/templates/{qa,evidence-report,codereview,verdict}.md`
- `plugins/sdd-composy/references/{execution,quality,evidence,verification}.md`
- `plugins/sdd-composy/scripts/sdd_evidence.py`
- `tests/test_sdd_composy_quality.py`

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
