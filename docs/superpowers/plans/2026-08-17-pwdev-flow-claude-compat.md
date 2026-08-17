# PWDEV Flow Native Claude Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `pwdev-flow` a first-class Claude Code plugin with seventeen native commands and a native Claude fleet while preserving the existing Codex implementation and one portable Flow artifact protocol.

**Architecture:** Keep skills, references, artifacts, audit, dashboard, and teardown semantics in a shared package. Add thin Claude command adapters and split privileged fleet execution into explicit Codex and Claude engine adapters behind shared launch/run cores; runtime identity is bound in fleet state and cannot be changed by configuration or environment.

**Tech Stack:** Claude Code 2.1.233 plugin manifests and commands, Codex plugin manifests and skills, Bash 3.2-compatible shell, `claude -p`, `codex exec`, Git worktrees, Docker Compose, tmux, jq, Python 3 standard library, JSON Schema, and Python `unittest` subprocess tests.

**Spec:** `docs/superpowers/specs/2026-08-17-pwdev-flow-claude-compat-design.md`

## Global Constraints

- Claude fleet uses native `claude -p`; Codex fleet continues to use `codex exec`.
- Expose exactly seventeen Claude commands: `init`, `discover`, `design`, `plan`, `execute`, `review`, `verify`, `simplify`, `quick`, `product`, `memory`, `health`, `audit`, `maintenance`, `compat`, `delegate`, and `fleet`.
- Keep the semantic `flow_audit.py` trail shared and hook-free.
- Keep Claude and Codex privileged command construction in separate source files.
- Preserve the portable `.planning/flow` protocol across runtimes; bind runtime strictly only for operational fleet state.
- Base release version is `0.6.0`; only the Codex manifest receives a cachebuster suffix during Codex installation.
- Do not add Claude subagents, hooks, MCP servers, apps, or model-routing profiles.
- Use temporary Git repositories and closed fake executables for all fleet behavior tests. Never launch real Claude, Codex, Docker, tmux, provider, or network activity from tests.
- Preserve the reviewed containment, symlink, contract-hash, strict-status, branch-binding, process-group, audit-order, and ownership-unresolved invariants.
- Do not commit, push, create a PR, or stage files. The user explicitly withheld Git publication authorization.
- Apply manual edits with `apply_patch`. Run formatters only for mechanical formatting after the relevant tests are green.

---

## File structure and responsibilities

| File or directory | Responsibility |
|---|---|
| `plugins/pwdev-flow/.claude-plugin/plugin.json` | Native Claude plugin identity and semantic version. |
| `plugins/pwdev-flow/commands/*.md` | Seventeen thin Claude entry adapters; no duplicated workflow semantics. |
| `plugins/pwdev-flow/scripts/fleet-common.sh` | Shared path, state, audit, and process-ownership primitives. |
| `plugins/pwdev-flow/scripts/fleet-engine-codex.sh` | Fixed Codex preflight and exact dangerous command array. |
| `plugins/pwdev-flow/scripts/fleet-engine-claude.sh` | Fixed Claude preflight, exact `claude -p` command array, and structured-output extraction. |
| `plugins/pwdev-flow/scripts/fleet-launch-core.sh` | Runtime-neutral validation, reservation, worktree, Compose, tmux, ACTIVE, and audit lifecycle. |
| `plugins/pwdev-flow/scripts/fleet-run-core.sh` | Runtime-neutral stage loop, correction bound, result validation, commit, recovery, and audit lifecycle. |
| `plugins/pwdev-flow/scripts/fleet-up.sh` | Thin immutable Codex launcher calling `flow_fleet_launch codex`. |
| `plugins/pwdev-flow/scripts/claude-fleet-up.sh` | Thin immutable Claude launcher calling `flow_fleet_launch claude`. |
| `plugins/pwdev-flow/scripts/fleet-run.sh` | Thin immutable Codex runner calling `flow_fleet_run codex`. |
| `plugins/pwdev-flow/scripts/claude-fleet-run.sh` | Thin immutable Claude runner calling `flow_fleet_run claude`. |
| `plugins/pwdev-flow/scripts/fleet-dashboard.sh` | Read-only dashboard for explicitly bound Codex and Claude fleet members. |
| `plugins/pwdev-flow/scripts/fleet-teardown.sh` | Strict runtime-aware shutdown and optional merge authorization. |
| `plugins/pwdev-flow/references/*.md` | Shared portable contracts, including dual-runtime fleet and installation behavior. |
| `.claude-plugin/marketplace.json` | Primary Claude marketplace registration. |
| `README.md`, `README.pt-BR.md` | Public dual-runtime installation, command, and safety documentation. |
| `tests/test_flow_claude_compat.py` | Manifest, command adapter, marketplace, documentation, and interoperability contract. |
| `tests/test_flow_claude_fleet.py` | Claude engine, launcher, runner, runtime binding, recovery, audit, and teardown behavior. |
| `tests/flow_m5_fixtures.py` | Shared fake Claude/Codex binaries and complete dual-runtime fleet fixtures. |

The final package has fourteen scripts: the existing seven, two Claude wrappers, two shared cores, one shared helper, and two engine adapters.

---

### Task 1: Establish the Claude compatibility contract in RED

**Files:**
- Create: `tests/test_flow_claude_compat.py`
- Modify: `tests/test_pwdev_flow.py`
- Read: `plugins/pwdev-flow/.codex-plugin/plugin.json`
- Read: `plugins/pwdev-code/.claude-plugin/plugin.json`
- Read: `plugins/pwdev-code/commands/*.md`
- Read: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: approved spec and existing source package.
- Produces: structural constants `CLAUDE_COMMANDS`, `COMMAND_TO_SKILL`, `EXPECTED_SCRIPTS`, and release assertions consumed by later tasks.

- [ ] **Step 1: Define the exact command and script inventories**

Add literal constants to `tests/test_flow_claude_compat.py`:

```python
CLAUDE_COMMANDS = {
    "audit", "compat", "delegate", "design", "discover", "execute",
    "fleet", "health", "init", "maintenance", "memory", "plan",
    "product", "quick", "review", "simplify", "verify",
}

COMMAND_TO_SKILL = {
    name: f"flow-{name}" for name in CLAUDE_COMMANDS
}

EXPECTED_SCRIPTS = {
    "claude-fleet-run.sh",
    "claude-fleet-up.sh",
    "fleet-common.sh",
    "fleet-dashboard.sh",
    "fleet-engine-claude.sh",
    "fleet-engine-codex.sh",
    "fleet-launch-core.sh",
    "fleet-run-core.sh",
    "fleet-run.sh",
    "fleet-teardown.sh",
    "fleet-up.sh",
    "flow_audit.py",
    "migrate_legacy.py",
    "run-agent.sh",
}
```

- [ ] **Step 2: Write manifest and adapter failures**

Add tests that require:

```python
def test_claude_manifest_is_native_and_hook_free(self):
    manifest = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text())
    self.assertEqual(manifest["name"], "pwdev-flow")
    self.assertEqual(manifest["version"], "0.6.0")
    self.assertFalse({"hooks", "mcpServers", "apps"} & manifest.keys())

def test_every_claude_command_maps_to_one_portable_skill(self):
    command_files = {p.stem: p for p in (PLUGIN / "commands").glob("*.md")}
    self.assertEqual(set(command_files), CLAUDE_COMMANDS)
    for name, path in command_files.items():
        text = path.read_text()
        self.assertIn("$ARGUMENTS", text)
        self.assertEqual(text.count("$ARGUMENTS"), 1)
        self.assertIn(
            f"${{CLAUDE_PLUGIN_ROOT}}/skills/{COMMAND_TO_SKILL[name]}/SKILL.md",
            text,
        )
```

Also assert standard frontmatter has `description`, optional `argument-hint` is a string, every mapped skill exists, and the adapter instructs Claude to read the skill completely rather than copying its procedure.

- [ ] **Step 3: Write marketplace, README, version, and inventory failures**

Require:

- primary `.claude-plugin/marketplace.json` has one `pwdev-flow` entry with source `./plugins/pwdev-flow`, category `workflow`, and `strict: true`;
- English and Portuguese READMEs contain a plugin-table entry, installation commands, all seventeen slash-command names, native Claude fleet wording, native Codex fleet wording, and semantic hook-free audit wording;
- Claude manifest is exactly `0.6.0`;
- Codex version matches `^0\.6\.0(?:\+codex\.\d{14})?$`;
- package contains exactly the fourteen script names above;
- package contains seventeen skills, seventeen commands, sixteen or more shared references, and three templates;
- no hooks/MCP/apps directory or manifest field exists.

- [ ] **Step 4: Add Markdown resource-link validation for command adapters**

Parse every literal `${CLAUDE_PLUGIN_ROOT}/...` path in `commands/*.md`, strip the prefix, and assert the target exists under `plugins/pwdev-flow`. Reject parent traversal and absolute paths outside `${CLAUDE_PLUGIN_ROOT}`.

- [ ] **Step 5: Run the new structural contract and observe RED**

Run:

```bash
python3 -m unittest tests.test_flow_claude_compat tests.test_pwdev_flow -v
```

Expected: failures identify the missing Claude manifest, missing seventeen commands, absent marketplace/README registration, old `0.5.0` base, and missing seven dual-runtime scripts. Existing unrelated structural assertions remain green.

- [ ] **Step 6: Record the Task 1 snapshot without committing**

Record the two test-file SHA-256 hashes, the exact RED count, and `git status --short` in the execution ledger. Do not stage or commit.

---

### Task 2: Add the Claude manifest and seventeen thin command adapters

**Files:**
- Create: `plugins/pwdev-flow/.claude-plugin/plugin.json`
- Create: `plugins/pwdev-flow/commands/audit.md`
- Create: `plugins/pwdev-flow/commands/compat.md`
- Create: `plugins/pwdev-flow/commands/delegate.md`
- Create: `plugins/pwdev-flow/commands/design.md`
- Create: `plugins/pwdev-flow/commands/discover.md`
- Create: `plugins/pwdev-flow/commands/execute.md`
- Create: `plugins/pwdev-flow/commands/fleet.md`
- Create: `plugins/pwdev-flow/commands/health.md`
- Create: `plugins/pwdev-flow/commands/init.md`
- Create: `plugins/pwdev-flow/commands/maintenance.md`
- Create: `plugins/pwdev-flow/commands/memory.md`
- Create: `plugins/pwdev-flow/commands/plan.md`
- Create: `plugins/pwdev-flow/commands/product.md`
- Create: `plugins/pwdev-flow/commands/quick.md`
- Create: `plugins/pwdev-flow/commands/review.md`
- Create: `plugins/pwdev-flow/commands/simplify.md`
- Create: `plugins/pwdev-flow/commands/verify.md`
- Test: `tests/test_flow_claude_compat.py`

**Interfaces:**
- Consumes: `CLAUDE_COMMANDS` and `COMMAND_TO_SKILL` from Task 1.
- Produces: native Claude plugin manifest and command contract available to marketplace, docs, and installation tasks.

- [ ] **Step 1: Create the Claude manifest with base version 0.6.0**

Use this schema-shaped content, with final prose copied from the approved design:

```json
{
  "name": "pwdev-flow",
  "displayName": "PWDEV Flow — Portable Spec-Driven Development",
  "version": "0.6.0",
  "description": "Portable, approval-gated software development for Claude Code and Codex, with shared artifacts, semantic audit, guarded delegation, and isolated native fleets.",
  "author": {
    "name": "Paulo Soares",
    "url": "https://github.com/soarescbm"
  },
  "homepage": "https://github.com/pwdev-solucoes/pwdev-claude-marketplace",
  "repository": "https://github.com/pwdev-solucoes/pwdev-claude-marketplace",
  "license": "Apache-2.0",
  "keywords": [
    "claude-code", "codex", "workflow", "spec-driven",
    "audit", "fleet", "delegation", "portable"
  ]
}
```

Do not add `hooks`, `mcpServers`, `apps`, agents, configuration, or runtime selection fields.

- [ ] **Step 2: Create a single canonical command-adapter shape**

Each command follows this exact behavioral template, with command-specific description and argument hint:

```markdown
---
description: Initialize or resume the portable PWDEV Flow workspace
argument-hint: "[--resume]"
---

# /pwdev-flow:init

Read `${CLAUDE_PLUGIN_ROOT}/skills/flow-init/SKILL.md` completely, including every directly required reference. Execute that skill as the active Claude Code adapter. Preserve the portable `.planning/flow` protocol and identify this adapter as `claude` wherever the skill records the initializing runtime.

User arguments: $ARGUMENTS
```

The only occurrences of workflow steps stay in the portable skill/reference files. Do not paste their procedures into commands.

- [ ] **Step 3: Add all seventeen adapters with exact mappings**

Use these argument hints:

| Command | Hint |
|---|---|
| `init` | `[--resume]` |
| `discover` | `<feature description>` |
| `design` | `<feature-slug>` |
| `plan` | `<feature-slug>` |
| `execute` | `<plan-path>` |
| `review` | `[path-or-ref]` |
| `verify` | `<feature-slug>` |
| `simplify` | `[feature-slug]` |
| `quick` | `<bounded task>` |
| `product` | `<product request>` |
| `memory` | `<capture|query|list> [arguments]` |
| `health` | `[full|workspace|deps]` |
| `audit` | `<record|summary|events|verify> [arguments]` |
| `maintenance` | `<inventory|archive|summarize> [arguments]` |
| `compat` | `<inspect|plan|migrate> [arguments]` |
| `delegate` | `<provider> <read|write> <task>` |
| `fleet` | `<slug...>|--status|--teardown <slug> [--merge]` |

Descriptions state the user outcome, not internal implementation.

- [ ] **Step 4: Run focused structural tests**

Run:

```bash
python3 -m unittest \
  tests.test_flow_claude_compat.ClaudeCompatibilityTests.test_claude_manifest_is_native_and_hook_free \
  tests.test_flow_claude_compat.ClaudeCompatibilityTests.test_every_claude_command_maps_to_one_portable_skill -v
```

Expected: both pass. Marketplace, README, version, and script-inventory tests remain RED for their owning tasks.

- [ ] **Step 5: Validate the source package with Claude Code**

Run:

```bash
claude plugin validate --strict plugins/pwdev-flow
```

Expected: exit 0 with no warning about the manifest or command frontmatter. If the locally installed CLI rejects a field, fix the manifest to the documented Claude schema without adding runtime-exclusive behavior.

- [ ] **Step 6: Review Task 2 without committing**

Inspect every adapter for exactly one `$ARGUMENTS`, exact skill path, no copied workflow, no secret filename, and no runtime-selection parameter. Record hashes and review result in the ledger.

---

### Task 3: Refactor the existing Codex fleet behind fixed shared-core interfaces

**Files:**
- Create: `plugins/pwdev-flow/scripts/fleet-common.sh`
- Create: `plugins/pwdev-flow/scripts/fleet-engine-codex.sh`
- Create: `plugins/pwdev-flow/scripts/fleet-launch-core.sh`
- Create: `plugins/pwdev-flow/scripts/fleet-run-core.sh`
- Modify: `plugins/pwdev-flow/scripts/fleet-up.sh`
- Modify: `plugins/pwdev-flow/scripts/fleet-run.sh`
- Modify: `plugins/pwdev-flow/scripts/fleet-dashboard.sh`
- Modify: `plugins/pwdev-flow/scripts/fleet-teardown.sh`
- Modify: `tests/test_flow_fleet_lifecycle.py`
- Modify: `tests/test_flow_fleet_runner.py`
- Modify: `tests/flow_m5_fixtures.py`

**Interfaces:**
- Produces: `flow_fleet_launch(runtime, slugs...)`, `flow_fleet_run(runtime, slug, worktree)`, `flow_engine_build_command(...)`, and member field `runtime`.
- Preserves: existing `fleet-up.sh <slug...>` and `fleet-run.sh <slug> <worktree>` Codex interfaces and exact Codex command vector.
- Consumed by: Claude adapters in Tasks 4–5.

- [ ] **Step 1: Add characterization tests before moving production code**

Add tests that assert the current Codex behavior literally:

```python
def test_codex_wrapper_binds_codex_runtime_and_exact_engine(self):
    result = self.run_fleet_up("demo")
    self.assertEqual(result.returncode, 0)
    member = self.read_member("demo")
    self.assertEqual(member["runtime"], "codex")

def test_codex_stage_vector_remains_exact_after_core_split(self):
    argv = self.fake_codex_argv()
    self.assertEqual(argv[:3], [
        "exec", "--dangerously-bypass-approvals-and-sandbox", "--ephemeral"
    ])
    self.assertEqual(argv.count("--dangerously-bypass-approvals-and-sandbox"), 1)
```

Before production changes, the first test must fail because `runtime` is absent; all existing security regressions must still pass.

- [ ] **Step 2: Define shared helper functions without engine commands**

`fleet-common.sh` exposes only these runtime-neutral interfaces:

| Function | Inputs | Required result |
|---|---|---|
| `flow_runtime_is_valid` | one string | exit 0 only for literal `codex` or `claude` |
| `flow_require_runtime` | expected, actual | sanitized fatal error unless the literals match |
| `flow_require_safe_chain` | canonical root, relative path, expected leaf type | walk every component with `lstat`, reject symlink/wrong type, and prove containment |
| `flow_atomic_publish` | source temporary, exact destination | require same safe parent and atomically rename without replacing an unowned type |
| `flow_emit_fleet_audit` | action, skill, phase, status, relative target, sanitized detail JSON | invoke `flow_audit.py` best-effort and preserve the lifecycle result |
| `flow_ensure_group_absent` | owned PID, owned PGID, grace count | bounded TERM, KILL escalation, wait, group-absence proof, and nonzero return if unresolved |

Transplant the already reviewed implementations from the current launcher/runner into these interfaces without changing their ordering or failure semantics. Delete each old copy only after the corresponding existing lifecycle/runner regression passes against the shared function. This file must contain neither engine command construction nor an environment-selected runtime.

- [ ] **Step 3: Isolate the exact Codex engine adapter**

`fleet-engine-codex.sh` exposes:

```bash
flow_engine_runtime() { printf '%s\n' codex; }
flow_engine_preflight() { command -v codex >/dev/null 2>&1; }
flow_engine_build_command() {
  FLOW_ENGINE_COMMAND=(
    codex exec
    --dangerously-bypass-approvals-and-sandbox
    --ephemeral
    --cd "$FLOW_WORKTREE"
    --output-schema "$FLOW_SCHEMA"
    --output-last-message "$FLOW_RESULT_TMP"
    "$FLOW_PROMPT"
  )
}
```

Use the exact current option ordering required by existing tests. Reject extra engine arguments. The adapter does not accept runtime from config, state, or environment.

- [ ] **Step 4: Extract launch and run cores with explicit positional runtime**

`fleet-launch-core.sh` defines `flow_fleet_launch()` and `fleet-run-core.sh` defines `flow_fleet_run()`. Their first function argument is copied immediately into a readonly local and validated against `codex|claude`. Engine adapter selection is a closed `case` over that readonly argument:

```bash
case "$flow_runtime" in
  codex) source "$FLOW_SCRIPT_DIR/fleet-engine-codex.sh" ;;
  claude) source "$FLOW_SCRIPT_DIR/fleet-engine-claude.sh" ;;
esac
[ "$(flow_engine_runtime)" = "$flow_runtime" ] || flow_die "engine binding mismatch"
```

Portable config cannot override `flow_runtime`. Member state includes `runtime`, and every subsequent read validates exact equality.

- [ ] **Step 5: Replace existing public Codex scripts with immutable wrappers**

`fleet-up.sh` becomes:

```bash
#!/usr/bin/env bash
set -euo pipefail
FLOW_SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
source "$FLOW_SCRIPT_DIR/fleet-launch-core.sh"
flow_fleet_launch codex "$@"
```

`fleet-run.sh` uses the same shape with `flow_fleet_run codex "$@"`. The wrappers never inspect configuration before binding runtime.

- [ ] **Step 6: Make dashboard and teardown require explicit runtime state**

Member validation requires `.runtime == "codex" or .runtime == "claude"`. Dashboard adds a Runtime column. Teardown validates member runtime before any Docker/tmux/merge action and passes it only to runtime-neutral cleanup/audit; it never launches an engine.

Legacy member files without `runtime` fail as malformed operational state and require explicit human recovery. Portable non-fleet artifacts remain compatible.

- [ ] **Step 7: Run the complete existing Codex suite**

Run:

```bash
python3 -m unittest \
  tests.test_flow_fleet_lifecycle \
  tests.test_flow_fleet_runner \
  tests.test_flow_delegation \
  tests.test_flow_operations \
  tests.test_pwdev_flow
```

Expected: all existing cases plus new Codex runtime-binding cases pass; only the known managed-sandbox socket skip is permitted. No fake Claude invocation exists yet.

- [ ] **Step 8: Run a security-focused mutation review**

Temporarily alter the test fixture or a copied script under `/tmp` to attempt `runtime=claude` through config/environment while invoking `fleet-up.sh`; prove the wrapper still records `codex`. Confirm removing the engine-runtime equality check makes a permanent test fail, then restore the source. Record the proof without committing.

---

### Task 4: Implement the native Claude engine and runner in RED → GREEN

**Files:**
- Create: `plugins/pwdev-flow/scripts/fleet-engine-claude.sh`
- Create: `plugins/pwdev-flow/scripts/claude-fleet-run.sh`
- Create: `tests/test_flow_claude_fleet.py`
- Modify: `plugins/pwdev-flow/scripts/fleet-run-core.sh`
- Modify: `plugins/pwdev-flow/templates/fleet-result.schema.json`
- Modify: `tests/flow_m5_fixtures.py`

**Interfaces:**
- Consumes: `flow_fleet_run claude` and shared process/state helpers from Task 3.
- Produces: fixed Claude command array and normalized result JSON matching `fleet-result.schema.json`.

- [ ] **Step 1: Add a complete fake Claude executable**

Extend the fixture so fake `claude`:

- writes each argv element on its own line;
- records current working directory and process group;
- optionally spawns a TERM-resistant descendant;
- emits a literal Claude JSON envelope;
- supports controlled exit, malformed output, missing structured output, timeout, and signal modes.

A success envelope is:

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "structured_output": {
    "stage": "plan",
    "status": "OK",
    "verdict": "APPROVED",
    "summary": "stage complete",
    "files": [".planning/flow/phases/demo/plans/01-demo.md"]
  }
}
```

Expected values are literals in each test, not derived by production helpers.

- [ ] **Step 2: Write Claude vector and isolation RED tests**

Require the exact prefix and singleton safety flag:

```python
self.assertEqual(argv[:4], [
    "-p",
    "--dangerously-skip-permissions",
    "--no-session-persistence",
    "--output-format",
])
self.assertEqual(argv[4], "json")
self.assertIn("--json-schema", argv)
self.assertIn("--append-system-prompt", argv)
self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", argv)
self.assertNotIn("codex", argv)
```

Also assert one prompt positional argument, no `--add-dir`, no plugin/config injection, and no arbitrary extra arguments.

- [ ] **Step 3: Write result normalization and failure RED tests**

Tests require:

- `.structured_output` is extracted to an owned same-directory temporary;
- the extracted object, not the Claude envelope, is validated by the shared schema;
- missing/malformed/contradictory envelope fails before commit;
- nonzero Claude exit is preserved;
- a stale prior result cannot satisfy a new run;
- result stage/slug/contract identity matches the bound member and requested stage.

- [ ] **Step 4: Write runtime mismatch and process ownership RED tests**

Run `claude-fleet-run.sh` with a member bound to Codex and require zero fake invocation. Repeat the existing HUP, TERM, leader-exit-with-descendant, and unresolved-ownership cases against fake Claude. Require group absence before validation, commit, status, audit, next stage, or lock release.

- [ ] **Step 5: Run Claude runner tests and observe RED**

Run:

```bash
python3 -m unittest tests.test_flow_claude_fleet.ClaudeFleetRunnerTests -v
```

Expected: failures identify missing `fleet-engine-claude.sh` and `claude-fleet-run.sh`; fixture-only envelope tests pass.

- [ ] **Step 6: Implement the fixed Claude engine adapter**

`fleet-engine-claude.sh` exposes the same three functions as the Codex engine. Build exactly:

```bash
FLOW_ENGINE_COMMAND=(
  claude
  -p
  --dangerously-skip-permissions
  --no-session-persistence
  --output-format json
  --json-schema "$FLOW_SCHEMA_JSON"
  --append-system-prompt "$FLOW_SYSTEM_PROMPT"
  "$FLOW_PROMPT"
)
```

`FLOW_SCHEMA_JSON` is the compact validated content of the packaged schema. Do not accept model, tools, directories, agents, settings, plugins, MCPs, or extra CLI arguments from project configuration.

- [ ] **Step 7: Normalize Claude output before shared validation**

After the owned process group is proven absent, parse the fresh captured envelope with jq:

```bash
jq -e '
  .type == "result" and
  .subtype == "success" and
  .is_error == false and
  (.structured_output | type == "object")
  | .structured_output
' "$FLOW_ENGINE_CAPTURE" > "$FLOW_RESULT_TMP"
```

Then use the same schema/semantic validation and atomic result publication as Codex. Parsing failure publishes a safe failure outcome only after process absence.

- [ ] **Step 8: Add the immutable Claude runner wrapper**

`claude-fleet-run.sh` sources `fleet-run-core.sh` and calls `flow_fleet_run claude "$@"`. It contains no Codex flag, engine selector, or project-provided options.

- [ ] **Step 9: Run focused GREEN and Codex regression**

Run:

```bash
python3 -m unittest tests.test_flow_claude_fleet.ClaudeFleetRunnerTests -v
python3 -m unittest tests.test_flow_fleet_runner -v
```

Expected: both modules pass. The known sandbox skip applies only where the existing fixture already declares it.

- [ ] **Step 10: Review Task 4 security boundaries**

Inspect both engine files side-by-side. Require that the Claude file contains no Codex bypass literal and the Codex file contains no Claude bypass literal. Require tests to fail if the engine filenames or runtime-return values are swapped.

---

### Task 5: Implement the Claude launcher and dual-runtime lifecycle

**Files:**
- Create: `plugins/pwdev-flow/scripts/claude-fleet-up.sh`
- Modify: `plugins/pwdev-flow/scripts/fleet-launch-core.sh`
- Modify: `plugins/pwdev-flow/scripts/fleet-dashboard.sh`
- Modify: `plugins/pwdev-flow/scripts/fleet-teardown.sh`
- Modify: `tests/test_flow_claude_fleet.py`
- Modify: `tests/test_flow_fleet_lifecycle.py`
- Modify: `tests/flow_m5_fixtures.py`

**Interfaces:**
- Consumes: Claude runner/engine from Task 4 and launch core from Task 3.
- Produces: `claude-fleet-up.sh <slug...>` and runtime-aware dashboard/teardown behavior.

- [ ] **Step 1: Write pre-mutation launcher RED tests**

Require zero branch, worktree, central member, Docker, and tmux mutation when:

- `claude` is missing;
- only `codex` exists;
- the wrapper is invoked with a runtime option or runtime environment variable;
- config contains a runtime field attempting `codex`;
- contracts, branch, paths, capacity, or packaged Claude runner are invalid.

- [ ] **Step 2: Write successful launch and tmux-vector RED tests**

A successful fake launch must record:

```json
{
  "runtime": "claude",
  "status": "ACTIVE"
}
```

The exact tmux payload must call `claude-fleet-run.sh` with slug and canonical worktree as distinct arguments. It must not contain `fleet-run.sh`, `codex`, shell evaluation, or unquoted concatenation.

- [ ] **Step 3: Write dashboard and teardown dual-runtime RED tests**

Require dashboard rows to display `claude` or `codex`. Teardown must:

- accept a valid Claude member and complete normal stop/merge rules;
- reject absent/unknown/mismatched runtime before Docker/tmux/merge;
- validate the same strict terminal status and base branch for both runtimes;
- emit sanitized `fleet_teardown` detail containing runtime but no absolute path;
- preserve recoverable state on conflict or runtime mismatch.

- [ ] **Step 4: Write cross-runtime isolation RED tests**

Launch a Claude member, then attempt to run the Codex wrapper on its worktree; require zero Codex invocation. Launch a Codex member and attempt the Claude wrapper; require zero Claude invocation. Changing only `.planning/flow/config.json` must not change either result.

- [ ] **Step 5: Run lifecycle tests and observe RED**

Run:

```bash
python3 -m unittest tests.test_flow_claude_fleet.ClaudeFleetLifecycleTests -v
```

Expected: failures identify missing Claude launcher and missing runtime-aware dashboard/teardown branches.

- [ ] **Step 6: Add the immutable Claude launcher wrapper**

`claude-fleet-up.sh` mirrors the Codex wrapper but calls `flow_fleet_launch claude "$@"`. The launch core uses the bound runtime to select the packaged runner filename and engine preflight from a closed case.

- [ ] **Step 7: Persist and validate runtime throughout lifecycle**

Member publication adds `runtime`. Local status/result records also include runtime when they represent a fleet outcome. Validation requires exact agreement among wrapper runtime, member runtime, local state, and dashboard/teardown target before side effects.

Do not add runtime as an authorization gate for portable non-fleet phase, memory, audit, health, migration, or product artifacts.

- [ ] **Step 8: Render dry-run and live paths from the same bound values**

Dry-run output names the selected fixed wrapper, runtime, member fields, contract hashes, base binding, atomic publications, Compose/tmux commands, and audit timing. Running the rendered safe plan against fakes must match live state and argv without launching real tools.

- [ ] **Step 9: Run complete dual-runtime lifecycle suites**

Run:

```bash
python3 -m unittest \
  tests.test_flow_claude_fleet \
  tests.test_flow_fleet_lifecycle \
  tests.test_flow_fleet_runner -v
```

Expected: all Claude and Codex lifecycle/runner cases pass with only the existing managed-sandbox socket skip.

- [ ] **Step 10: Review Task 5 recovery and destructive boundaries**

Verify every negative test asserts unchanged external sentinels and zero fake side effects. Inspect that cleanup removes only exact owned targets and never uses recursive deletion, unresolved variables, broad globs, or a runtime-derived executable path.

---

### Task 6: Document and test portable interoperability, audit, and migration

**Files:**
- Modify: `plugins/pwdev-flow/references/artifacts.md`
- Modify: `plugins/pwdev-flow/references/audit.md`
- Modify: `plugins/pwdev-flow/references/fleet.md`
- Modify: `plugins/pwdev-flow/references/safety.md`
- Modify: `plugins/pwdev-flow/references/workflow.md`
- Modify: `plugins/pwdev-flow/references/migration.md`
- Modify: `plugins/pwdev-flow/skills/flow-fleet/SKILL.md`
- Modify: `plugins/pwdev-flow/skills/flow-init/SKILL.md`
- Modify: `plugins/pwdev-flow/skills/flow-compat/SKILL.md`
- Modify: `tests/test_flow_claude_compat.py`
- Modify: `tests/test_flow_operations.py`

**Interfaces:**
- Consumes: runtime field and scripts from Tasks 3–5.
- Produces: public cross-runtime contract and behavioral interoperability evidence.

- [ ] **Step 1: Write interoperability RED tests using real portable artifacts**

Create a temporary `.planning/flow/config.json` initialized with `runtime: "codex"`, then invoke the portable initialization/inspection logic as Claude and require all unknown fields and artifacts to remain readable. Repeat Claude → Codex. Assert only the adapter marker changes when initialization explicitly updates it.

- [ ] **Step 2: Write audit RED tests for runtime-safe details**

Record Claude and Codex fleet events through the real `flow_audit.py`. Require allowed semantic fields, relative targets, valid runtime enum, and rejection of nested/literal prompts, models, private paths, or engine argv. Existing disabled/no-op, malformed-log, and secret-key tests remain green.

- [ ] **Step 3: Update the artifact and workflow references**

Document that portable state can move between runtimes and that `config.runtime` records the last initializing adapter without granting fleet authorization. Document the strict operational member runtime and exact paths for both runners.

- [ ] **Step 4: Update fleet and safety references**

Include both exact privileged vectors, explicit wrapper names, preflight requirements, runtime mismatch behavior, process-group proof order, audit timing, dashboard Runtime column, teardown rules, and the prohibition against config/environment runtime switching.

- [ ] **Step 5: Update init, fleet, and compatibility skills**

- `flow-init` sets the current adapter marker while preserving unknown fields.
- `flow-fleet` routes Claude hosts to `claude-fleet-up.sh` and Codex hosts to `fleet-up.sh`; it never accepts a user-selected runtime flag.
- `flow-compat` documents migration from `pwdev-code` into portable Flow artifacts without rewriting legacy source.

- [ ] **Step 6: Run operations and compatibility tests**

Run:

```bash
python3 -m unittest \
  tests.test_flow_claude_compat \
  tests.test_flow_operations \
  tests.test_flow_delegation -v
```

Expected: all interoperability, audit, migration, adapter, and standalone delegation tests pass. Marketplace/README/version tests may remain RED until Tasks 7–8.

- [ ] **Step 7: Validate every source skill**

Run the official `quick_validate.py` over all seventeen `skills/*` directories with the known local PyYAML dependency path. Expected: exactly seventeen `Skill is valid!` results.

---

### Task 7: Register and document PWDEV Flow in the Claude marketplace

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`
- Modify: `README.pt-BR.md`
- Test: `tests/test_flow_claude_compat.py`

**Interfaces:**
- Consumes: final Claude manifest, commands, scripts, and docs from Tasks 2–6.
- Produces: discoverable Claude marketplace entry and public installation/usage contract.

- [ ] **Step 1: Add the marketplace entry with exact source and version agreement**

Append one entry following `pwdev-code` conventions:

```json
{
  "name": "pwdev-flow",
  "displayName": "PWDEV Flow — Portable Claude Code + Codex Workflow",
  "source": "./plugins/pwdev-flow",
  "description": "Portable approval-gated development with 17 Claude commands and 17 Codex skills, shared artifacts, semantic audit, guarded delegation, and isolated native fleets.",
  "category": "workflow",
  "tags": ["claude-code", "codex", "workflow", "spec-driven", "fleet", "audit"],
  "strict": true
}
```

Do not edit or reorder unrelated marketplace entries.

- [ ] **Step 2: Add plugin-table rows to both READMEs**

Describe version `0.6.0`, dual runtime, seventeen Claude commands, seventeen Codex skills, semantic audit, guarded delegation, and native isolated fleets. Keep existing plugin rows unchanged.

- [ ] **Step 3: Add concise English and Portuguese usage sections**

Each section contains:

- Claude marketplace install/update commands;
- Codex local marketplace install/update commands used by this repository;
- the full seventeen-command list;
- shared `.planning/flow` portability statement;
- Claude-native versus Codex-native fleet statement;
- dangerous fleet isolation warning;
- semantic hook-free audit statement;
- restart/new-session requirement after plugin updates.

- [ ] **Step 4: Run strict Claude validation on plugin and marketplace**

Run:

```bash
claude plugin validate --strict plugins/pwdev-flow
claude plugin validate --strict .claude-plugin/marketplace.json
```

Expected: both exit 0 with no warning.

- [ ] **Step 5: Run all structural/documentation tests**

Run:

```bash
python3 -m unittest tests.test_flow_claude_compat tests.test_pwdev_flow -v
```

Expected: all tests pass except the Task 8-owned Codex base/cachebuster version gate if source is still `0.5.0+codex...`.

- [ ] **Step 6: Review public claims against production**

For every README claim, point to its manifest, command, script, or test evidence. Remove claims that are not executable. Confirm no README instructs Claude to run the Codex fleet or Codex to run the Claude fleet.

---

### Task 8: Release version 0.6.0, validate, install both runtimes, and review

**Files:**
- Modify: `plugins/pwdev-flow/.codex-plugin/plugin.json`
- Verify: `plugins/pwdev-flow/.claude-plugin/plugin.json`
- Modify: `docs/superpowers/plans/2026-08-17-pwdev-flow-claude-compat.md` checkbox markers only after evidence exists
- Report: `.superpowers/sdd/2026-08-17-pwdev-flow-claude-compat/release-report.md`

**Interfaces:**
- Consumes: complete green source from Tasks 1–7.
- Produces: installed Claude `0.6.0`, installed Codex `0.6.0+codex.<UTC timestamp>`, source/install validation evidence, and final independent review.

- [ ] **Step 1: Set both manifests to the shared base release**

Use `apply_patch` to set the Codex manifest base version to `0.6.0`. Require the Claude manifest already equals `0.6.0`. Verify descriptions agree on product identity while runtime-only fields remain schema-specific.

- [ ] **Step 2: Run the complete source suite before installation**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py'
```

Expected: all Codex and Claude tests pass; only the existing managed-sandbox socket skip is permitted. Confirm fake logs prove no real autonomous runtime or network activity.

- [ ] **Step 3: Run source syntax, content, and official validators**

Run:

```bash
for shell_script in plugins/pwdev-flow/scripts/*.sh; do bash -n "$shell_script" || exit 1; done
python3 -c 'import ast; from pathlib import Path; [ast.parse(p.read_text(), filename=str(p)) for p in Path("plugins/pwdev-flow/scripts").glob("*.py")]'
claude plugin validate --strict plugins/pwdev-flow
claude plugin validate --strict .claude-plugin/marketplace.json
```

Also run the official Codex plugin validator and all seventeen skill validators, JSON parsing, Markdown-link tests, placeholder/trailing-whitespace scans, `.DS_Store` inventory, and `git diff --check`.

- [ ] **Step 4: Apply exactly one Codex cachebuster after the final source change**

Record the base manifest version and SHA-256, then run exactly once:

```bash
python3 /Users/paulosoares/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py \
  plugins/pwdev-flow
```

Expected transition: `0.6.0` to `0.6.0+codex.<14-digit UTC timestamp>`. Do not run this utility again in the release attempt unless a later source change invalidates the candidate; such a change starts a separately recorded release attempt.

- [ ] **Step 5: Install and validate Codex from the configured local marketplace**

Run the approved local command:

```bash
codex plugin add pwdev-flow@pwdev-flow
```

Derive the installed cache path independently from the final Codex manifest. Require source/cache `diff -qr` empty, exact package inventories, source/cache plugin validation, and seventeen source/cache skill validations.

- [ ] **Step 6: Add or update the local Claude marketplace and install PWDEV Flow**

First inspect configured marketplaces:

```bash
claude plugin marketplace list
```

If this repository path is absent, request the required external-state approval and run:

```bash
claude plugin marketplace add /Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace
```

Then install or update at local scope as appropriate:

```bash
claude plugin install pwdev-flow@pwdev-claude-marketplace --scope local
```

If already installed, use `claude plugin update pwdev-flow@pwdev-claude-marketplace`. Do not uninstall unrelated plugins or edit user configuration manually.

- [ ] **Step 7: Inspect the installed Claude component inventory**

Run:

```bash
claude plugin details pwdev-flow@pwdev-claude-marketplace
claude plugin list
```

Require version `0.6.0`, seventeen commands, no agents/hooks/MCPs, and source paths belonging to the installed package. Validate the installed copy directly with `claude plugin validate --strict <installed-path>` after resolving its exact path from Claude's own details/list output.

- [ ] **Step 8: Smoke-test both adapters without autonomous execution**

Use validation/details and command discovery only. Do not invoke fleet launch or standalone external providers. Confirm Claude exposes `/pwdev-flow:init` through `/pwdev-flow:fleet` and Codex exposes all seventeen `pwdev-flow:*` skills in a new task/session.

- [ ] **Step 9: Run one final fresh full suite after both installations**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py'
```

Expected: all tests pass with the same single sandbox skip. Re-run source/install parity and validators after the suite; no source file may change after the final cachebuster.

- [ ] **Step 10: Request an independent read-only code review**

Give the reviewer the spec, this plan, exact source/test tree hashes, release report, installed paths, and all runtime-boundary invariants. The reviewer checks manifest/command correctness, vector isolation, state runtime binding, process ownership, path safety, audit timing, strict teardown, tests, docs, and installation evidence.

Critical or Important findings block release. Fixes require new RED tests, fresh full validation, a new recorded Codex cachebuster attempt, reinstall of both runtimes, and scoped re-review.

- [ ] **Step 11: Persist release evidence and complete only verified checkboxes**

Write `.superpowers/sdd/2026-08-17-pwdev-flow-claude-compat/release-report.md` with:

- versions and manifest hashes;
- test counts and the exact skip;
- validators and inventories;
- source/install paths and parity;
- Claude marketplace/install commands and component inventory;
- Codex cachebuster exactly-once evidence;
- review verdict and open non-blocking concerns;
- Git/status proof and confirmation that no real autonomous process ran.

Change plan checkbox markers only after their evidence exists. Do not commit, stage, push, merge, or create a PR.

---

## Final acceptance checklist

- [ ] Seventeen Claude commands exist and map one-to-one to portable skills.
- [ ] Claude manifest and primary marketplace validate strictly.
- [ ] Claude fleet uses only its fixed `claude -p` engine adapter.
- [ ] Codex fleet retains only its fixed `codex exec` engine adapter.
- [ ] Runtime identity is bound across member, runner, status, dashboard, audit, and teardown.
- [ ] Shared non-fleet artifacts continue across Claude and Codex.
- [ ] All path, symlink, contract, process, state, merge, and audit safety regressions pass for both runtimes.
- [ ] README files accurately document installation, commands, portability, and fleet safety.
- [ ] Source, installed Codex, and installed Claude packages validate.
- [ ] Full suite passes before and after installation with no unexpected skip.
- [ ] Independent review has no Critical or Important finding.
- [ ] No commit, staging, push, PR, real autonomous runtime, provider, Docker, tmux, or network test execution occurred.
