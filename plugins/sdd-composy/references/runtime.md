# SDD Composy runtime contract

SDD Composy ships one runtime-neutral core for Claude Code, Codex, Hermes Agent, and OpenCode.
The shared core is the single source of workflow meaning; runtime adapters only expose entry
points, map host tools, and construct provider-specific command vectors.

## Package discovery

Every runtime consumes the same package roots:

| Root | Contract |
|---|---|
| `skills/` | Portable capability instructions and orchestration |
| `references/` | Lifecycle, artifacts, state, safety, runtime, and OKF rules |
| `scripts/` | Deterministic shared operations |
| `templates/` | Runtime-neutral generated content |
| `schemas/` | Validation contracts for operational JSON and evidence |

Paths written as `scripts/...`, `references/...`, or `templates/...` in a skill are relative to the
plugin root: `${CLAUDE_PLUGIN_ROOT}` on Claude Code, the installed plugin on Codex and Hermes, and
the parent of the linked skill folder on OpenCode.

| Runtime | Discovery | Entry points |
|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` | `commands/<name>.md` as `/sdd-composy:<name>`; each command routes to the shared skill, passes the user's arguments and repository context, and returns the shared result unchanged |
| Codex | `.codex-plugin/plugin.json`, `"skills": "./skills/"` | `$sdd-<name>` (the skill's `name`); native skill discovery is the adapter |
| Hermes Agent | `.hermes-plugin/plugin.yaml`; the bootstrap registers the 17 skills and adds the tool mapping on the first turn | `skill_view("sdd-<name>")`; tool mapping in [hermes-tools.md](hermes-tools.md), read only when the runtime is Hermes |
| OpenCode | no plugin mechanism: `.opencode-plugin/install.py` links the 17 skill folders into `~/.config/opencode/skills/` (or `<project>/.opencode/skills/` with `--project`) and generates `command/sdd-<name>.md` beside them; OpenCode also reads `.agents/skills/` and `.claude/skills/` | the native `skill` tool and `/sdd-<name>` commands. Link only, never copy: the skills reach `scripts/` and `references/` through the link |

## Adapter boundary

A thin adapter must not duplicate lifecycle rules, gate logic, artifact formats, schema
semantics, safety policy, or orchestration from the shared core. It must not create
runtime-specific variants of human or operational artifacts. Changes to workflow meaning
belong in the shared skills or references and therefore take effect in every runtime.

At session entry, identify the current runtime from available host tools, never from persisted
project state. Use only tools exposed by that host. The shared runner owns process groups, stage
ordering, result validation, locks, durable state, and cleanup; adapters do not own lifecycle
truth. No adapter falls back to another provider.

## Automation vectors (LOOP and FLEET)

| Runtime | Vector | Engine adapters |
|---|---|---|
| Claude Code | `claude -p` with JSON output | `scripts/loop-engine-claude.py`, `scripts/fleet/engine-claude.sh` |
| Codex | `codex exec` with an output schema and result file | `scripts/loop-engine-codex.py`, `scripts/fleet/engine-codex.sh` |
| Hermes Agent | `hermes -z <prompt> --in <worktree>`, only after independently established isolation or the user's specific consent | `scripts/loop-engine-hermes.py`, `scripts/fleet/engine-hermes.sh` |
| OpenCode | `opencode run --format json --dir <worktree> --auto` (observed in OpenCode 1.18.31; earlier releases used `--dangerously-skip-permissions`) | **none in this release**: LOOP and FLEET on OpenCode are `NOT_RUN`, never a fallback |

Hermes Kanban is not implemented, so it is unavailable rather than an alternate orchestration
route. Fleet Compose is runtime-neutral; its central file, project name, and teardown identity are
defined in [fleet.md](fleet.md).

## State, language, and compatibility

The current runtime may be recorded as provenance, but it cannot control readability or
ownership. All runtimes read the same human contracts under `tasks/prd-<slug>/` and operational
state under `.planning/sdd-composy/`. Markdown owns intent, narrative acceptance contracts,
and human approvals; validated JSON owns current operational state. Operational task documents
are bundles shaped as `{ "tasks": [...] }`. A synchronization conflict requires an explicit
authority choice; editing `state.json` or task JSON to imitate approval is unsupported.
Switching runtimes resumes from the last valid durable transition and does not reinterpret
approvals or repeat a successfully published stage.

The persisted language (`pt-BR` or `en-US`) applies to human-facing prose only; see
[the language contract](language.md). Init distinguishes a safe `.claude -> .agents` link
(`symlink`) from a preserved real `.claude` directory with a regular `AGENTS.md` bridge
(`existing_directory`). Other destinations or ancestor symlinks fail closed.

Packaged discovery and offline tests establish installed adapter support, not acceptance of a
real provider. Real acceptance on any runtime remains unclaimed until the acceptance harness runs.
Permission, authentication, cost, or availability failures are `BLOCKED`/`NOT_RUN`, not success.

## Independence

The plugin must not depend at runtime on `pwdev-flow` or `pwdev-feat`. Their installed files,
commands, skills, state, and configuration are neither prerequisites nor fallbacks. Any
behavior reused conceptually by SDD Composy is defined inside this plugin's shared core.
