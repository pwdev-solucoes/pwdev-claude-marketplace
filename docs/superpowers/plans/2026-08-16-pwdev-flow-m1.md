# PWDEV Flow M1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Deliver an installable native Codex plugin with four workflow skills and a runtime-neutral protocol.

**Architecture:** Keep Codex discovery and triggering in a thin adapter while storing workflow semantics in shared references. Use structural tests to enforce the plugin contract and prevent Claude-specific runtime dependencies from entering the new implementation.

**Tech Stack:** Codex plugin JSON, Markdown skills, YAML frontmatter, Python `unittest` structural tests.

**Spec:** `docs/superpowers/specs/2026-08-16-pwdev-flow-m1-design.md`

## Global Constraints

- Create a new `plugins/pwdev-flow` directory; do not modify `plugins/pwdev-code`.
- Use `pwdev-flow` as the folder name and manifest name.
- Do not add hooks, apps, or MCP declarations in M1.
- Do not depend on `${CLAUDE_PLUGIN_ROOT}`, Claude's `Task` tool, `subagent_type`, or Claude model names.
- Never commit automatically.

---

### Task 1: Structural contract

**Files:**
- Create: `tests/test_pwdev_flow.py`

**Interfaces:**
- Consumes: the M1 design acceptance criteria.
- Produces: executable checks for manifest shape, skills, references, links, forbidden terms, and marketplace registration.

- [x] Write Python `unittest` cases that describe the required plugin structure.
- [x] Run `python3 -m unittest tests/test_pwdev_flow.py -v` and confirm failure because `plugins/pwdev-flow` does not exist.

### Task 2: Plugin scaffold and neutral protocol

**Files:**
- Create: `plugins/pwdev-flow/.codex-plugin/plugin.json`
- Create: `plugins/pwdev-flow/references/workflow.md`
- Create: `plugins/pwdev-flow/references/artifacts.md`
- Create: `plugins/pwdev-flow/references/collaboration.md`
- Create: `plugins/pwdev-flow/references/safety.md`

**Interfaces:**
- Consumes: the Codex plugin manifest contract and M1 design.
- Produces: a discoverable plugin and stable reference paths used by every M1 skill.

- [x] Generate the plugin skeleton with the official scaffold utility.
- [x] Replace scaffold metadata with PWDEV Flow metadata and Codex interface prompts.
- [x] Write concise runtime-neutral workflow, artifact, collaboration, and safety contracts.
- [x] Run the structural test and confirm only missing skills or marketplace assertions remain.

### Task 3: Vertical workflow skills

**Files:**
- Create: `plugins/pwdev-flow/skills/flow-init/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-init/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-quick/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-quick/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-review/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-review/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-verify/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-verify/agents/openai.yaml`

**Interfaces:**
- Consumes: the four reference contracts through relative Markdown links.
- Produces: intent-triggered initialization, bounded delivery, review, and adversarial verification workflows.

- [x] Initialize each skill with the official skill utility and UI metadata.
- [x] Replace generated content with concise imperative workflows and explicit output contracts.
- [x] Validate each skill with `quick_validate.py`.
- [x] Run the structural test and confirm only marketplace assertions remain.

### Task 4: Repository-local Codex marketplace

**Files:**
- Create: `.agents/plugins/marketplace.json`

**Interfaces:**
- Consumes: the plugin identifier and repository plugin location.
- Produces: an `AVAILABLE`, `ON_INSTALL`, `Developer Tools` marketplace entry for `pwdev-flow`.

- [x] Generate the repository marketplace entry with the official plugin scaffold utility.
- [x] Verify the entry uses `./plugins/pwdev-flow` and leaves `.claude-plugin/marketplace.json` untouched.

### Task 5: Verification

**Files:**
- Modify only files from Tasks 1–4 if verification exposes defects.

**Interfaces:**
- Consumes: all M1 artifacts.
- Produces: fresh validation evidence and a bounded diff summary.

- [x] Run `python3 -m unittest tests/test_pwdev_flow.py -v`.
- [x] Run the official plugin validator against `plugins/pwdev-flow`.
- [x] Run `quick_validate.py` for all four skills.
- [x] Inspect `git diff -- plugins/pwdev-flow .agents/plugins/marketplace.json tests/test_pwdev_flow.py docs/superpowers`.
- [x] Confirm no tracked or untracked file under `plugins/pwdev-code` was created or modified by this increment.
