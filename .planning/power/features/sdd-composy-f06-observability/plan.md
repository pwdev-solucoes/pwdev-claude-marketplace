# SDD Composy F06 Trace, Status, and Quick — Plan
Status: APPROVED
Spec: .planning/power/features/sdd-composy/spec.md
Updated: 2026-09-08

For agentic workers: execute this with pwdev-power:power-execute.

## Goal
Add an integrity-checked semantic event trail, rebuildable trace projection, consolidated read-only status, and a five-file quick path.

## Architecture
`events.jsonl` is append-only history, `trace.json` is a derived graph, and status is computed without writes. Quick creates normal task/trace records under a bounded contract.

## Tech Stack
Python 3 standard library, JSON/JSONL, Markdown skills, Python `unittest`.

## Global Constraints
- Never edit `trace.json` directly or repair an invalid audit trail automatically.
- Semantic events are recorded only after the represented action succeeds.
- Never record prompts, output dumps, environment variables, secrets, models, or private paths.
- Status is strictly read-only.
- Quick touches at most 5 implementation files and excludes architecture, migrations, destructive work, and unknown verification.
- Quick contracts and reports conform to OKF v0.2 and remain linked from the bundle index.

## File Structure
- `plugins/sdd-composy/scripts/{sdd_trace,sdd_status}.py`
- `plugins/sdd-composy/references/{trace,status,quick}.md`
- `plugins/sdd-composy/skills/{sdd-trace,sdd-status,sdd-quick}/`
- `plugins/sdd-composy/commands/{trace,status,quick}.md`
- `plugins/sdd-composy/templates/{quick-contract,quick-report}.md`
- `tests/test_sdd_composy_observability.py`

## Task 01 — Append-only semantic events
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_trace.py`, `plugins/sdd-composy/references/trace.md`, `tests/test_sdd_composy_observability.py`
Interfaces:
  Consumes: validated semantic event arguments
  Produces: `record`, `events`, `summary`, and `verify` over `trace/events.jsonl`
Steps:
- [ ] Add failing tests for disabled no-op, safe append, invalid JSONL, prohibited keys, unsafe targets, and append preservation.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_observability` and observe failure.
- [ ] Implement safe directory traversal, mode-restricted append, event validation, and queries.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 02 — Trace projection
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_trace.py`, `tests/test_sdd_composy_observability.py`
Interfaces:
  Consumes: valid PRD/stories/TechSpec/tasks/evidence identifiers and valid semantic events
  Produces: deterministic `build`, `query`, and `verify-projection` for `trace.json`, including evidence artifact hashes
Steps:
- [ ] Add failing graph tests for RF-US-SC-CA-task-test-evidence-manifest-artifact-hash-verdict links, dangling IDs, duplicate IDs, and deterministic rebuild.
- [ ] Run the focused test and observe failure.
- [ ] Implement graph assembly, source-event count binding, atomic publication, and queries.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 03 — Trace skill and adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-trace/SKILL.md`, `plugins/sdd-composy/skills/sdd-trace/agents/openai.yaml`, `plugins/sdd-composy/commands/trace.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `sdd_trace.py record|events|summary|verify|build|query|verify-projection`
  Produces: portable `$sdd-trace` and `/sdd-composy:trace`
Steps:
- [ ] Add failing route and safety tests.
- [ ] Run the structural test.
- [ ] Implement skill, metadata, and adapter.
- [ ] Run structural and observability tests.
- [ ] Commit only when explicitly authorized.

## Task 04 — Consolidated status helper
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_status.py`, `plugins/sdd-composy/references/status.md`, `tests/test_sdd_composy_observability.py`
Interfaces:
  Consumes: config, global state, task files, trace integrity, loop records, and fleet records
  Produces: read-only text/JSON snapshot with exact next valid action
Steps:
- [ ] Add failing tests for uninitialized, active, blocked, divergent, looping, fleet, malformed, and no-write behavior.
- [ ] Run the focused test and observe failure.
- [ ] Implement aggregation with source confidence and actionable mismatch reporting.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 05 — Status skill and adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-status/SKILL.md`, `plugins/sdd-composy/skills/sdd-status/agents/openai.yaml`, `plugins/sdd-composy/commands/status.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `sdd_status.py [--feature] [--tasks] [--fleet] [--json]`
  Produces: portable `$sdd-status` and `/sdd-composy:status`
Steps:
- [ ] Add failing read-only and output-contract tests.
- [ ] Run the structural test.
- [ ] Implement skill, metadata, and adapter.
- [ ] Run structural and observability tests.
- [ ] Commit only when explicitly authorized.

## Task 06 — Quick path
Complexity: high
Files: `plugins/sdd-composy/templates/quick-contract.md`, `plugins/sdd-composy/templates/quick-report.md`, `plugins/sdd-composy/references/quick.md`, `plugins/sdd-composy/skills/sdd-quick/SKILL.md`, `tests/test_sdd_composy_observability.py`
Interfaces:
  Consumes: bounded objective, acceptance criteria, allowed files, and known verification commands
  Produces: Q-ID task record, contract, report, trace events, and verified verdict
Steps:
- [ ] Add failing tests for the five-file gate, forbidden categories, TDD, escalation, normal task registration, and evidence.
- [ ] Run the focused test and observe failure.
- [ ] Implement templates, reference, skill, and task/trace integration contract.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 07 — Quick adapter and integrated validation
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-quick/agents/openai.yaml`, `plugins/sdd-composy/commands/quick.md`, `tests/test_sdd_composy.py`, `tests/test_sdd_composy_tasks.py`
Interfaces:
  Consumes: `$sdd-quick` contract from Task 06
  Produces: Claude adapter and verified quick-to-full escalation boundary
Steps:
- [ ] Add failing discovery, adapter, and escalation integration tests.
- [ ] Run structural and task tests.
- [ ] Implement metadata and thin adapter, then connect any missing task transition.
- [ ] Re-run structural, task, and observability tests.
- [ ] Commit only when explicitly authorized.
