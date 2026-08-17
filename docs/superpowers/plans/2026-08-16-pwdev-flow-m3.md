# PWDEV Flow Marco 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Complete the PWDEV Flow native Codex lifecycle with seven new workflow skills and six shared protocol references.

**Architecture:** Keep skill entry points concise and move portable schemas and gates into root references. Extend the existing structural test so missing skills, references, phase contracts, or stale manifest metadata fail deterministically.

**Tech Stack:** Codex plugin JSON, Markdown skills, YAML UI metadata, Python `unittest` structural tests.

**Spec:** `docs/superpowers/specs/2026-08-16-pwdev-flow-m3-design.md`

## Global Constraints

- Modify only `plugins/pwdev-flow`, `tests/test_pwdev_flow.py`, and this Marco 3 design/plan.
- Preserve the repository marketplace entry without hand-editing it.
- Keep hooks, apps, MCP servers, audit, fleet, and external delegation out of Marco 3.
- Work inline and do not create subagents because the user did not request delegation.
- Do not commit, push, create branches, or alter unrelated local changes.

---

### Task 1: Extend the executable contract

**Files:**
- Modify: `tests/test_pwdev_flow.py`

**Interfaces:**
- Consumes: Marco 3 skill names, reference names, artifact invariants, and manifest requirements.
- Produces: failing tests that distinguish a complete Marco 3 plugin from M1.

- [x] Add the seven Marco 3 skills and six references to the expected sets.
- [x] Add assertions for full lifecycle phases, eight specification sections, memory types, roadmap hierarchy, approval-gated simplification, inline-default execution, and no automatic commits.
- [x] Run `python3 -m unittest tests/test_pwdev_flow.py -v` and confirm failure because Marco 3 files do not exist.

### Task 2: Add the neutral protocols

**Files:**
- Create: `plugins/pwdev-flow/references/discovery.md`
- Create: `plugins/pwdev-flow/references/specification.md`
- Create: `plugins/pwdev-flow/references/planning.md`
- Create: `plugins/pwdev-flow/references/execution.md`
- Create: `plugins/pwdev-flow/references/product.md`
- Create: `plugins/pwdev-flow/references/memory.md`
- Modify: `plugins/pwdev-flow/references/workflow.md`
- Modify: `plugins/pwdev-flow/references/artifacts.md`
- Modify: `plugins/pwdev-flow/references/collaboration.md`

**Interfaces:**
- Consumes: the design's paths, gates, schemas, and safety policy.
- Produces: portable contracts referenced by all full-lifecycle skills.

- [x] Write each reference with exact inputs, outputs, gates, failure behavior, and artifact paths.
- [x] Expand lifecycle and artifact references without duplicating detailed schemas.
- [x] Run the structural tests and confirm failures are limited to missing skills or manifest version.

### Task 3: Create the discovery, design, and planning adapters

**Files:**
- Create: `plugins/pwdev-flow/skills/flow-discover/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-discover/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-design/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-design/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-plan/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-plan/agents/openai.yaml`

**Interfaces:**
- Consumes: discovery, specification, planning, memory, artifact, and safety references.
- Produces: approved requirements, central specifications, wave maps, and atomic task plans.

- [x] Initialize the three skills with the official skill utility and exact UI metadata.
- [x] Replace generated content with concise imperative phase procedures.
- [x] Validate each skill with `quick_validate.py`.

### Task 4: Create execution and simplification adapters

**Files:**
- Create: `plugins/pwdev-flow/skills/flow-execute/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-execute/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-simplify/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-simplify/agents/openai.yaml`

**Interfaces:**
- Consumes: approved plans, execution protocol, collaboration policy, memory, and safety.
- Produces: verified task changes, execution summaries, advice requests, and approval-gated simplification reports.

- [x] Initialize both skills with the official skill utility and exact UI metadata.
- [x] Implement serial execution, blocker handling, fresh evidence, and no-commit defaults.
- [x] Implement separate `ANALYZE` and `APPLY` simplification passes with explicit proposal approval.
- [x] Validate both skills with `quick_validate.py`.

### Task 5: Create product and memory adapters

**Files:**
- Create: `plugins/pwdev-flow/skills/flow-product/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-product/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-memory/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-memory/agents/openai.yaml`

**Interfaces:**
- Consumes: product and memory schemas plus the artifact and safety policies.
- Produces: approval-gated PRDs, traceable roadmaps, and curated memory entries.

- [x] Initialize both skills with the official skill utility and exact UI metadata.
- [x] Implement PRD interview, approval gate, roadmap hierarchy, and traceability rules.
- [x] Implement capture, list, show, link, supersede, and relevance selection operations.
- [x] Validate both skills with `quick_validate.py`.

### Task 6: Update and verify the plugin

**Files:**
- Modify: `plugins/pwdev-flow/.codex-plugin/plugin.json`

**Interfaces:**
- Consumes: completed Marco 3 plugin and existing local marketplace registration.
- Produces: a `0.3.0` plugin with a single local Codex cachebuster and fresh validation evidence.

- [x] Set the base version to `0.3.0` and update plugin descriptions and starter prompts for the full lifecycle.
- [x] Run `update_plugin_cachebuster.py` against `plugins/pwdev-flow`.
- [x] Run `python3 -m unittest tests/test_pwdev_flow.py -v`.
- [x] Run the official plugin validator and all eleven skill validators.
- [x] Scan links, placeholders, forbidden runtime terms, frontmatter, and scoped status.
- [x] Confirm unrelated dirty files have exactly the same status as before Marco 3.
