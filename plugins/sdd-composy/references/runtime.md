# SDD Composy runtime contract

SDD Composy ships one runtime-neutral core for Claude Code, Codex, and Hermes Agent. The
shared core is the single source of workflow meaning; runtime adapters only expose entry
points, map host tools, and construct provider-specific command vectors.

## Package discovery

All three runtimes consume these same package roots:

| Root | Contract |
|---|---|
| `skills/` | Portable capability instructions and orchestration |
| `references/` | Lifecycle, artifacts, state, safety, runtime, and OKF rules |
| `scripts/` | Deterministic shared operations |
| `templates/` | Runtime-neutral generated content |
| `schemas/` | Validation contracts for operational JSON and evidence |

Claude Code discovers `.claude-plugin/plugin.json`. Its user-facing entry points are
`commands/<name>.md`, invoked as `/sdd-composy:<name>`. Each command selects the corresponding
shared skill, passes the user's arguments and repository context, maps only host tool names,
and returns the shared result.

Codex discovers `.codex-plugin/plugin.json`, whose `"skills": "./skills/"` declaration exposes
the same skills as `$sdd-composy-<name>`. Native skill discovery is its adapter.

Hermes discovers `.hermes-plugin/plugin.yaml`. Its bootstrap registers the shared skills and
adds the tool mapping on the first turn; a capability is selected with
`skill_view("sdd-composy:skill-name")`. Automated LOOP uses
`hermes -z <prompt> --in <repository-root>`, and fleet uses the same vector with the member's
independent worktree. Automation is refused unless isolation is independently established or
the user gives specific consent. No adapter falls back to another provider. Hermes Kanban is
not implemented, so it is unavailable rather than an alternate orchestration route.

## Adapter boundary

A thin adapter must not duplicate lifecycle rules, gate logic, artifact formats, schema
semantics, safety policy, or orchestration from the shared core. It must not create
runtime-specific variants of human or operational artifacts. Changes to workflow meaning
belong in the shared skills or references and therefore take effect in every runtime.

At session entry, identify the current runtime from available host tools, never from persisted
project state. Use only tools exposed by that host. Provider vectors are deliberately distinct:
Claude Code uses `claude -p` with JSON output, Codex uses `codex exec` with an output schema and
result file, and Hermes uses `hermes -z ... --in`. The shared runner owns process groups, stage
ordering, result validation, locks, durable state, and cleanup; adapters do not own lifecycle
truth.

## State, language, and compatibility

The current runtime may be recorded as provenance, but it cannot control readability or
ownership. All runtimes read the same human contracts under `tasks/prd-<slug>/` and operational
state under `.planning/sdd-composy/`. Markdown owns intent, narrative acceptance contracts,
and human approvals; validated JSON owns current operational state. Operational task documents
are bundles shaped as `{ "tasks": [...] }`. A synchronization conflict requires an explicit
authority choice; editing `state.json` or task JSON to imitate approval is unsupported.
Switching runtimes resumes from the last valid durable transition and does not reinterpret
approvals or repeat a successfully published stage.

The persisted language is exactly `pt-BR` or `en-US`. It applies to human-facing governance
prose only; IDs, JSON keys, enum values, filenames, commands, and user evidence are not
translated. Init distinguishes a safe `.claude -> .agents` link (`symlink`) from a preserved
real `.claude` directory with a regular `AGENTS.md` bridge (`existing_directory`). Other
destinations or ancestor symlinks fail closed.

Packaged discovery and offline tests establish installed adapter support, not acceptance of a
real provider. Real Hermes, Codex, and Claude Code acceptance remains unclaimed until the
acceptance harness runs. Permission, authentication, cost, or availability failures are
`BLOCKED`/`NOT_RUN`, not success.

## Independence

The plugin must not depend at runtime on `pwdev-flow` or `pwdev-feat`. Their installed files,
commands, skills, state, and configuration are neither prerequisites nor fallbacks. Any
behavior reused conceptually by SDD Composy is defined inside this plugin's shared core.
