# SDD Composy F02 Init and Map — Plan
Status: APPROVED
Spec: .planning/power/features/sdd-composy/spec.md
Updated: 2026-09-08

For agentic workers: execute this with pwdev-power:power-execute.

## Goal
Initialize SDD state and governance safely, then produce an evidence-based codebase map usable by downstream skills.

## Architecture
Python helpers own deterministic writes. Skills own intent and reporting. Templates are copied only to absent destinations; brownfield conflicts produce a plan instead of overwrites.

## Tech Stack
Python 3 standard library, Markdown templates, symlinks, Python `unittest`.

## Global Constraints
- `AGENTS.md` is canonical; `CLAUDE.md` points readers to it.
- Create `.claude -> .agents` only after compatibility and collision preflight.
- Never overwrite existing governance files, symlinks, `.agents`, or `.claude` paths.
- Never read `.env`, credentials, tokens, private keys, certificates, or existing fleet environment files.
- A re-run is idempotent.
- The map records the source commit and is observation, never architectural intent.
- Initialization records an OKF actor ID and creates the `tasks/index.md` bundle root without overwriting an existing index.

## File Structure
- `plugins/sdd-composy/templates/{AGENTS,CLAUDE}.md`
- `plugins/sdd-composy/templates/rules/{00-sdd-composy,architecture,testing,workflow}.md`
- `plugins/sdd-composy/scripts/{sdd_init,sdd_map}.py`
- `plugins/sdd-composy/skills/{sdd-init,sdd-map}/SKILL.md`
- `plugins/sdd-composy/skills/{sdd-init,sdd-map}/agents/openai.yaml`
- `plugins/sdd-composy/commands/{init,map}.md`
- `tests/test_sdd_composy_runtime.py`

## Task 01 — Governance root templates
Complexity: medium
Files: `plugins/sdd-composy/templates/AGENTS.md`, `plugins/sdd-composy/templates/CLAUDE.md`, `tests/test_sdd_composy_runtime.py`
Interfaces:
  Consumes: F01 workflow and artifact contracts
  Produces: renderable canonical governance templates
Steps:
- [ ] Add failing tests for required codebase, commands, workflow, gates, artifact, and safety sections.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_runtime` and observe failure.
- [ ] Write templates with explicit render variables and no unresolved scaffold placeholders in installed output.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 02 — Rule templates
Complexity: medium
Files: `plugins/sdd-composy/templates/rules/00-sdd-composy.md`, `plugins/sdd-composy/templates/rules/architecture.md`, `plugins/sdd-composy/templates/rules/testing.md`, `plugins/sdd-composy/templates/rules/workflow.md`, `tests/test_sdd_composy_runtime.py`
Interfaces:
  Consumes: governance contract from Task 01
  Produces: segmented `.agents/rules` template set
Steps:
- [ ] Add failing rule-discovery and responsibility tests.
- [ ] Run the focused test and observe missing rules.
- [ ] Implement non-duplicative rule templates linked by `AGENTS.md`.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 03 — Safe initialization helper
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_init.py`, `tests/test_sdd_composy_runtime.py`
Interfaces:
  Consumes: template root and F01 schemas
  Produces: `inspect`, `plan`, `apply`, and `verify` commands plus OKF v0.2 bundle initialization
Steps:
- [ ] Add failing temporary-repository tests for clean init, OKF actor/index creation, idempotence, file conflict, directory conflict, and unsafe symlink refusal.
- [ ] Run the focused test and observe expected failures.
- [ ] Implement repository-bound safe-path checks, atomic writes, template rendering, and `.claude -> .agents` creation.
- [ ] Ensure `apply` requires the exact plan token emitted by `plan` when conflicts exist.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 04 — Init skill and Claude adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-init/SKILL.md`, `plugins/sdd-composy/skills/sdd-init/agents/openai.yaml`, `plugins/sdd-composy/commands/init.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `sdd_init.py inspect|plan|apply|verify`
  Produces: portable `$sdd-init` and `/sdd-composy:init`
Steps:
- [ ] Add failing discovery, routing, and command-thinness tests.
- [ ] Run the structural test and observe failure.
- [ ] Write the skill, metadata, and thin command adapter.
- [ ] Re-run the structural test.
- [ ] Commit only when explicitly authorized.

## Task 05 — Codebase map helper
Complexity: high
Files: `plugins/sdd-composy/scripts/sdd_map.py`, `plugins/sdd-composy/references/mapping.md`, `tests/test_sdd_composy_runtime.py`
Interfaces:
  Consumes: repository root and governance without secret files
  Produces: OKF v0.2 context concepts and `codebase.json` with commit, commands, modules, boundaries, and confidence
Steps:
- [ ] Add failing fixture tests for stack detection, manifest-derived commands, domain evidence, staleness, and secret exclusion.
- [ ] Run the focused test and observe failure.
- [ ] Implement adaptive read-only inventory and deterministic serialized output.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 06 — Map skill and Claude adapter
Complexity: medium
Files: `plugins/sdd-composy/skills/sdd-map/SKILL.md`, `plugins/sdd-composy/skills/sdd-map/agents/openai.yaml`, `plugins/sdd-composy/commands/map.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: `sdd_map.py` output contract
  Produces: portable `$sdd-map` and `/sdd-composy:map`
Steps:
- [ ] Add failing tests for read-only scope, output paths, staleness, and downstream routing.
- [ ] Run the structural test and observe failure.
- [ ] Implement skill, metadata, and command adapter.
- [ ] Re-run structural and runtime tests.
- [ ] Commit only when explicitly authorized.
