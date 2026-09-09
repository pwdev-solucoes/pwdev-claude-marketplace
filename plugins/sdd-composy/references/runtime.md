# SDD Composy runtime contract

SDD Composy ships one runtime-neutral core for Claude Code and Codex. The shared core is the single source of workflow meaning; runtime adapters only expose an entry point and translate host tool names.

## Package discovery

Both runtimes consume these same package roots:

| Root | Contract |
|---|---|
| `skills/` | Portable capability instructions and orchestration |
| `references/` | Lifecycle, artifacts, state, safety, runtime, and OKF rules |
| `scripts/` | Deterministic shared operations |
| `templates/` | Runtime-neutral generated content |
| `schemas/` | Validation contracts for operational JSON and evidence |

Claude Code discovers the package through `.claude-plugin/plugin.json`. Its user-facing entry points are `commands/<name>.md`, invoked as `/sdd-composy:<name>`. Each command is a thin adapter: it selects the corresponding shared skill, passes through the user's arguments and repository context, maps only the host's tool vocabulary, and returns the shared result.

Codex discovers the package through `.codex-plugin/plugin.json`, whose `"skills": "./skills/"` declaration exposes the same skills. A user invokes them as `$sdd-composy-<name>`. Codex needs no duplicate command body: native skill discovery is its adapter.

## Adapter boundary

A thin adapter must not duplicate lifecycle rules, gate logic, artifact formats, schema semantics, safety policy, or orchestration from the shared core. It must not create runtime-specific variants of human or operational artifacts. Changes to workflow meaning belong in the shared skills or references and therefore take effect in both runtimes.

At session entry, identify the current runtime from the available host tool surface, never from persisted project state. Then use only real tools exposed by that host; if a requested orchestration mechanism is unavailable, execute inline or report the limitation rather than inventing a tool call.

The current runtime may be recorded as provenance, but it cannot control readability or ownership. Claude Code and Codex read and update the same human contracts under `tasks/prd-<slug>/` and operational state under `.planning/sdd-composy/`. Switching runtimes resumes from the last valid durable transition and does not reinterpret approvals or repeat a successfully published stage.

## Independence

The plugin must not depend at runtime on `pwdev-flow` or `pwdev-feat`. Their installed files, commands, skills, state, and configuration are neither prerequisites nor fallbacks. Any behavior reused conceptually by SDD Composy is defined inside this plugin's shared core.
