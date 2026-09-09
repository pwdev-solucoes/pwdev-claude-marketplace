# SDD Composy F09 — Language-aware artifacts — Plan
Status: APPROVED
Spec: .planning/power/features/sdd-composy-f09-language/spec.md
Updated: 2026-09-09

For agentic workers: execute this with pwdev-power:power-execute.

## Goal
Persist and resolve the artifact language for both Claude and Codex without silently choosing when the language is unknown.

## Architecture
A shared language helper owns enum validation, persisted preference, structured init choices, and no-write behavior. Init is the only prompting entry point; artifact skills consume the helper and select human-facing labels/content while preserving machine contracts.

## Tech Stack
Python 3 standard library, Markdown templates, JSON, unittest.

## Global Constraints
- Never generate artifacts before language is resolved.
- Never translate machine keys, IDs, schemas, filenames, or command names.
- Invalid language values fail without mutation.
- All writes remain atomic and path-confined.

## File Structure
- `plugins/sdd-composy/scripts/sdd_language.py`
- `plugins/sdd-composy/scripts/sdd_init.py`
- `plugins/sdd-composy/references/language.md`
- `plugins/sdd-composy/skills/sdd-init/SKILL.md`
- `plugins/sdd-composy/commands/init.md`
- `tests/test_sdd_composy_language.py`

## Task 01 — Language resolver
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_language.py`, `plugins/sdd-composy/references/language.md`, `tests/test_sdd_composy_language.py`
Interfaces:
  Consumes: repository root and optional explicit `pt-BR|en-US` value.
  Produces: persisted preference, init-only choices, or `{status: not_initialized, next_action: run_init}` for consumers.
Steps:
- [ ] Add failing tests for init-only missing choice, valid, invalid, persisted, override, atomicity, downstream no-prompt, and not-initialized response.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_language` and observe failure.
- [ ] Implement confined atomic resolver.
- [ ] Re-run the focused test.
- [ ] Record report.

## Task 02 — Init integration
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_init.py`, `plugins/sdd-composy/skills/sdd-init/SKILL.md`, `plugins/sdd-composy/commands/init.md`, `tests/test_sdd_composy_language.py`
Interfaces:
  Consumes: resolver from Task 01.
  Produces: init language prompt/selection shared by Claude and Codex.
Steps:
- [ ] Add failing integration tests for explicit selection, missing prompt, invalid no-write, and persisted reuse.
- [ ] Run the focused language test and observe failure.
- [ ] Integrate init and adapters without duplicating policy.
- [ ] Re-run focused and structural tests.
- [ ] Record report.

## Task 03 — Artifact routing and final validation
Complexity: medium
Files: `plugins/sdd-composy/references/workflow.md`, `plugins/sdd-composy/README.md`, `plugins/sdd-composy/README.pt-BR.md`, `tests/test_sdd_composy.py`, `tests/test_sdd_composy_language.py`
Interfaces:
  Consumes: resolved language contract.
  Produces: documented PT-BR/EN-US artifact behavior and compatibility tests.
Steps:
- [ ] Add failing route/documentation tests.
- [ ] Implement shared routing guidance and bilingual docs.
- [ ] Run all language, structural, and full SDD Composy tests.
- [ ] Record final report.
