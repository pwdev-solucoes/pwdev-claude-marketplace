# SDD Composy F01 Foundation — Plan
Status: APPROVED
Spec: .planning/power/features/sdd-composy/spec.md
Updated: 2026-09-08

For agentic workers: execute this with pwdev-power:power-execute.

## Goal
Create the independently installable dual-runtime plugin skeleton, shared contracts, schemas, and structural validation.

## Architecture
Both runtimes discover the same `skills/`, `references/`, `scripts/`, `templates/`, and `schemas/`. Claude commands are thin adapters. Operational JSON is schema-versioned and human contracts remain Markdown.

## Tech Stack
Markdown, JSON Schema, Python 3 standard library, shell adapters, Python `unittest`.

## Global Constraints
- Plugin identifier and directory name are exactly `sdd-composy`.
- Support Claude Code and Codex from the same portable contracts.
- The plugin has no runtime dependency on `pwdev-flow` or `pwdev-feat`.
- Human contracts remain under `tasks/prd-<slug>/`.
- Operational state remains under `.planning/sdd-composy/`.
- Never read `.env`, credentials, tokens, private keys, certificates, or existing fleet environment files.
- Preserve unknown JSON fields during supported updates.
- Generated project Markdown targets OKF v0.2; `type` is required and unknown extension fields remain permitted.

## File Structure
- `plugins/sdd-composy/.claude-plugin/plugin.json`
- `plugins/sdd-composy/.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `plugins/sdd-composy/references/{workflow,artifacts,states,safety,runtime}.md`
- `plugins/sdd-composy/schemas/{config,state,tasks,trace,loop,fleet-member,fleet-result,evidence-manifest}.schema.json`
- `tests/test_sdd_composy.py`
- `plugins/sdd-composy/references/okf.md`
- `plugins/sdd-composy/scripts/sdd_okf.py`

## Task 01 — Scaffold and manifests
Complexity: low
Files: `plugins/sdd-composy/.claude-plugin/plugin.json`, `plugins/sdd-composy/.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: plugin identifier `sdd-composy`
  Produces: installable Claude/Codex manifests and marketplace registration
Steps:
- [ ] Add failing manifest and marketplace discovery tests.
- [ ] Run `python3 -m unittest tests.test_sdd_composy` and confirm the missing plugin failure.
- [ ] Scaffold both manifests and append marketplace entries without altering existing entries.
- [ ] Run the focused test and confirm it passes.
- [ ] Commit only when explicitly authorized.

## Task 02 — Workflow and artifact contracts
Complexity: medium
Files: `plugins/sdd-composy/references/workflow.md`, `plugins/sdd-composy/references/artifacts.md`, `plugins/sdd-composy/references/states.md`, `plugins/sdd-composy/references/safety.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: approved lifecycle and dual-root decision
  Produces: canonical lifecycle, artifact ownership, state transitions, and safety contract
Steps:
- [ ] Add failing tests for required lifecycle, roots, gates, and secret prohibitions.
- [ ] Run the focused suite and observe contract failures.
- [ ] Write the four shared references with no runtime-specific orchestration.
- [ ] Re-run the focused suite.
- [ ] Commit only when explicitly authorized.

## Task 03 — Runtime contract
Complexity: medium
Files: `plugins/sdd-composy/references/runtime.md`, `plugins/sdd-composy/README.md`, `plugins/sdd-composy/README.pt-BR.md`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: shared plugin layout from Task 01
  Produces: exact discovery and adapter rules for Claude Code and Codex
Steps:
- [ ] Add failing portability and documentation tests.
- [ ] Run the focused suite and observe failure.
- [ ] Document shared-core discovery and thin Claude adapter behavior in both languages.
- [ ] Re-run the focused suite.
- [ ] Commit only when explicitly authorized.

## Task 04 — Core schemas
Complexity: high
Files: `plugins/sdd-composy/schemas/config.schema.json`, `plugins/sdd-composy/schemas/state.schema.json`, `plugins/sdd-composy/schemas/tasks.schema.json`, `plugins/sdd-composy/schemas/trace.schema.json`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: state and artifact contracts from Task 02
  Produces: version-1 validation schemas for configuration, global state, task state, and trace projection
Steps:
- [ ] Add failing schema-shape and valid/invalid fixture tests.
- [ ] Run the focused suite and confirm missing-schema failures.
- [ ] Implement strict required fields, enums, identifier patterns, and extension-safe objects.
- [ ] Re-run the focused suite.
- [ ] Commit only when explicitly authorized.

## Task 05 — Autonomous, fleet, and evidence schemas
Complexity: high
Files: `plugins/sdd-composy/schemas/loop.schema.json`, `plugins/sdd-composy/schemas/fleet-member.schema.json`, `plugins/sdd-composy/schemas/fleet-result.schema.json`, `plugins/sdd-composy/schemas/evidence-manifest.schema.json`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: lifecycle states from Task 02
  Produces: loop/fleet operational contracts and a criterion-linked evidence manifest contract
Steps:
- [ ] Add failing tests for the 3-iteration default, terminal states, runtime/UI enums, evidence result/type separation, confined paths, and hashes.
- [ ] Run the focused suite and observe failures.
- [ ] Implement the three schemas and cross-field invariants testable by fixtures.
- [ ] Re-run the focused suite.
- [ ] Commit only when explicitly authorized.

## Task 06 — Structural validation
Complexity: medium
Files: `tests/test_sdd_composy.py`, `tests/test_marketplace_readmes.py`
Interfaces:
  Consumes: all F01 files
  Produces: green structural and marketplace validation commands for later phases
Steps:
- [ ] Extend tests to reject placeholders, broken relative links, divergent manifest versions, and unregistered skills.
- [ ] Run `python3 -m unittest tests.test_sdd_composy tests.test_marketplace_readmes`.
- [ ] Fix only F01 contract defects exposed by the tests.
- [ ] Re-run both modules and read the complete result.
- [ ] Commit only when explicitly authorized.

## Task 07 — OKF v0.2 contract and linter
Complexity: high
Files: `plugins/sdd-composy/references/okf.md`, `plugins/sdd-composy/scripts/sdd_okf.py`, `tests/test_sdd_composy.py`
Interfaces:
  Consumes: an SDD project artifact root and configured actor ID
  Produces: `lint`, `index`, and frontmatter validation for OKF v0.2 project documents
Steps:
- [ ] Add failing tests for required `type`, permissive extensions, generated/verified actors, ISO timestamps, sources, reserved index/log behavior, and broken-link reporting.
- [ ] Run `python3 -m unittest tests.test_sdd_composy` and observe failures.
- [ ] Implement OKF parsing and linting without requiring optional fields for base conformance.
- [ ] Add root-index generation with `okf_version: "0.2"` and progressive-disclosure entries.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.
