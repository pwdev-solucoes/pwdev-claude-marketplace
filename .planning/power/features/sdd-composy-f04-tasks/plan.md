# SDD Composy F04 Tasks and Synchronization — Plan
Status: APPROVED
Spec: .planning/power/features/sdd-composy/spec.md
Updated: 2026-09-08

For agentic workers: execute this with pwdev-power:power-execute.

## Goal
Create human task contracts and a deterministic operational task engine with dependency-safe transitions and conflict-first synchronization.

## Architecture
Markdown defines task intent; validated JSON owns operational status. `sdd_tasks.py` performs state transitions. `sdd_sync.py` compares representations and requires explicit conflict resolution.

## Tech Stack
Python 3 standard library, JSON, Markdown, Python `unittest`.

## Global Constraints
- Task IDs are stable and never renumbered after approval.
- A task cannot become `ready` until all dependencies are `complete`.
- A task cannot become `complete` without fresh tests, QA, review, verify, and trace consistency.
- Conflicting Markdown and JSON are never overwritten silently.
- All writes use same-directory temporary files and atomic replacement.
- Preserve unknown JSON fields during supported updates.
- Generated task Markdown is OKF v0.2 and links upstream concepts through `sources` and body links.

## File Structure
- `plugins/sdd-composy/templates/{tasks,task}.md`
- `plugins/sdd-composy/references/{tasks,synchronization}.md`
- `plugins/sdd-composy/scripts/{sdd_tasks,sdd_sync}.py`
- `plugins/sdd-composy/skills/{sdd-tasks,sdd-sync}/`
- `plugins/sdd-composy/commands/{tasks,sync}.md`
- `tests/test_sdd_composy_tasks.py`

## Task 01 — Human task contracts
Complexity: medium
Files: `plugins/sdd-composy/templates/tasks.md`, `plugins/sdd-composy/templates/task.md`, `plugins/sdd-composy/references/tasks.md`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: approved PRD, stories resolution, and TechSpec
  Produces: dependency-explicit task index and per-task contracts
Steps:
- [ ] Add failing tests for IDs, dependencies, RF/US/SC/CA/test links, allowed files, subtasks, and verification commands.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_tasks` and observe failure.
- [ ] Implement the two templates and task contract reference.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 02 — Task state core
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_tasks.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: F01 tasks schema
  Produces: `import`, `list`, `show`, and schema-verified serialization
Steps:
- [ ] Add failing fixture tests for import, stable IDs, unknown-field preservation, unsafe paths, and atomic writes.
- [ ] Run the focused test and observe failure.
- [ ] Implement parsing, schema-aligned validation, and deterministic output.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 03 — Dependency and transition engine
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_tasks.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: imported feature-task state from Task 02
  Produces: `next`, `start`, `block`, and `transition` with legal-state enforcement
Steps:
- [ ] Add failing tests for cycles, missing dependencies, ready selection, illegal transitions, blocked reasons, and rejected-to-ready recovery.
- [ ] Run the focused test and observe expected failures.
- [ ] Implement graph validation and exact transition guards.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 04 — Evidence and completion guards
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_tasks.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: task transition engine and evidence records
  Produces: guarded `qa_required`, `review_required`, `verify_required`, `complete`, and `skipped` transitions
Steps:
- [ ] Add failing tests for stale evidence, missing tests, blocking QA/review, rejected verification, unjustified skip, and valid completion.
- [ ] Run the focused test and observe failures.
- [ ] Implement completion predicates and timestamp validation.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 05 — Task skill and adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-tasks/SKILL.md`, `plugins/sdd-composy/skills/sdd-tasks/agents/openai.yaml`, `plugins/sdd-composy/commands/tasks.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `sdd_tasks.py import|list|next|start|block|transition|verify`
  Produces: portable `$sdd-tasks` and `/sdd-composy:tasks`
Steps:
- [ ] Add failing route and mutation-boundary tests.
- [ ] Run the structural test.
- [ ] Implement skill, metadata, and thin adapter.
- [ ] Run structural and task tests.
- [ ] Commit only when explicitly authorized.

## Task 06 — Divergence inspection and plan
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_sync.py`, `plugins/sdd-composy/references/synchronization.md`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: Markdown task contracts and JSON task state
  Produces: read-only `inspect` and deterministic `plan` with conflict classifications and confirmation token
Steps:
- [ ] Add failing tests for no-change, one-sided addition, changed identity, status divergence, and malformed source.
- [ ] Run the focused test and observe failure.
- [ ] Implement comparison without choosing a conflicting authority.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 07 — Explicit synchronization apply
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_sync.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: exact synchronization plan token from Task 06
  Produces: atomic `apply` of an explicitly selected resolution
Steps:
- [ ] Add failing tests for stale token, changed inputs, symlink destinations, explicit Markdown choice, explicit JSON choice, and post-apply verification.
- [ ] Run the focused test and observe failures.
- [ ] Implement guarded application and revalidation.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 08 — Sync skill and adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-sync/SKILL.md`, `plugins/sdd-composy/skills/sdd-sync/agents/openai.yaml`, `plugins/sdd-composy/commands/sync.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `sdd_sync.py inspect|plan|apply`
  Produces: portable `$sdd-sync` and `/sdd-composy:sync`
Steps:
- [ ] Add failing tests for read-only inspection and explicit apply approval.
- [ ] Run the structural test.
- [ ] Implement skill, metadata, and adapter.
- [ ] Run structural and task tests.
- [ ] Commit only when explicitly authorized.
