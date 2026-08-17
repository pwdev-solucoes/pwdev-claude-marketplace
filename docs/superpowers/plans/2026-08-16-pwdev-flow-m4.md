# PWDEV Flow Marco 4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add safe operational diagnostics, maintenance, semantic audit, and legacy migration to PWDEV Flow.

**Architecture:** Put deterministic audit and migration behavior in dependency-free Python scripts tested through subprocesses. Keep health, maintenance, audit, and compatibility UX in concise Codex skills backed by neutral references.

**Tech Stack:** Python 3 standard library, JSONL, Codex skills, Markdown references, YAML UI metadata, Python `unittest`.

**Spec:** `docs/superpowers/specs/2026-08-16-pwdev-flow-m4-design.md`

## Global Constraints

- Modify only PWDEV Flow source, its tests, and Marco 4 design/plan files.
- Do not hand-edit `.agents/plugins/marketplace.json`.
- Keep audit opt-in and semantic; do not add hooks to the manifest.
- Preserve all legacy files during migration and refuse target overwrite.
- Do not read or record secrets.
- Do not commit, push, create branches, or modify unrelated changes.

---

### Task 1: Define failing behavior contracts

**Files:**
- Modify: `tests/test_pwdev_flow.py`
- Create: `tests/test_flow_operations.py`

**Interfaces:**
- Consumes: Marco 4 skill, reference, audit, migration, compatibility, and version requirements.
- Produces: structural assertions and subprocess behavior tests with literal expected results.

- [x] Extend expected skills with `flow-health`, `flow-maintenance`, `flow-audit`, and `flow-compat`.
- [x] Extend expected references with `health.md`, `maintenance.md`, `audit.md`, and `migration.md`.
- [x] Require manifest base version `0.4.0` with one cachebuster.
- [x] Add real CLI tests for audit record/summary, disabled no-op, malformed log, and secret rejection.
- [x] Add real CLI tests for migration plan/apply, source preservation, target conflict, and secret exclusion.
- [x] Run both test modules and confirm failure because scripts and Marco 4 artifacts do not exist.

### Task 2: Implement deterministic scripts

**Files:**
- Create: `plugins/pwdev-flow/scripts/flow_audit.py`
- Create: `plugins/pwdev-flow/scripts/migrate_legacy.py`

**Interfaces:**
- `flow_audit.py --root <repo> record|summary|events|verify`
- `migrate_legacy.py --root <repo> plan|apply`

- [x] Implement audit configuration checks, action validation, secret rejection, atomic JSONL append, filters, summary, and integrity verification.
- [x] Run focused audit tests and confirm they pass.
- [x] Implement legacy mapping, dry-run JSON output, exclusive target creation, safe allowlist preservation, and migration metadata.
- [x] Run focused migration tests and confirm they pass.

### Task 3: Add operational references

**Files:**
- Create: `plugins/pwdev-flow/references/health.md`
- Create: `plugins/pwdev-flow/references/maintenance.md`
- Create: `plugins/pwdev-flow/references/audit.md`
- Create: `plugins/pwdev-flow/references/migration.md`
- Modify: `plugins/pwdev-flow/references/artifacts.md`
- Modify: `plugins/pwdev-flow/references/safety.md`

**Interfaces:**
- Consumes: deterministic script CLIs and Marco 4 safety constraints.
- Produces: exact operational modes, paths, gates, scoring rules, and migration mapping documentation.

- [x] Document read-only health checks and evidence-based score rules.
- [x] Document inventory, archive approval, and changelog merge rules.
- [x] Document JSONL schema, action vocabulary, command examples, and limitations.
- [x] Document non-destructive migration, supported mappings, conflicts, and legacy artifact handling.
- [x] Expand artifact and safety protocols with audit/archive/migration paths and secret-safe logging.

### Task 4: Add operational and compatibility skills

**Files:**
- Create: `plugins/pwdev-flow/skills/flow-health/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-health/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-maintenance/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-maintenance/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-audit/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-audit/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-compat/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-compat/agents/openai.yaml`
- Modify: `plugins/pwdev-flow/skills/flow-init/SKILL.md`

**Interfaces:**
- Consumes: Marco 4 references and scripts.
- Produces: operational user workflows, approved migration route, and legacy intent routing.

- [x] Initialize all four skills with the official utility and UI metadata.
- [x] Implement health as diagnosis-only with optional report persistence.
- [x] Implement maintenance modes with exact-target approval and no deletion.
- [x] Implement audit modes through the deterministic helper.
- [x] Implement supported legacy mappings and explicit unsupported results.
- [x] Add inspect/initialize/migrate routing to `flow-init`.
- [x] Validate all fifteen skills.

### Task 5: Version, install, and verify

**Files:**
- Modify: `plugins/pwdev-flow/.codex-plugin/plugin.json`

**Interfaces:**
- Consumes: completed Marco 4 plugin and existing `pwdev-flow` marketplace.
- Produces: installed `0.4.0+codex.<cachebuster>` source/cache parity.

- [x] Set base version `0.4.0` and update operational starter prompts.
- [x] Run `update_plugin_cachebuster.py` once.
- [x] Reinstall `pwdev-flow@pwdev-flow` from the existing local marketplace.
- [x] Run both test modules, official plugin validation, and all fifteen skill validators.
- [x] Verify source/cache equality, links, placeholders, whitespace, runtime neutrality, and unrelated status.
