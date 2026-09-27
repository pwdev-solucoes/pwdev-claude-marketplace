# Codex Tool Mapping

Inspect the tool surface actually exposed in the session. Resolve each capability to an
available tool instead of requiring a fixed name.

| Action skills request | Typical Codex capability |
|---|---|
| Read or search files | `exec_command` with `sed`, `rg`, or another read-only command |
| Create, replace, or edit a file | `apply_patch` |
| Run a command | `exec_command` |
| Ask the human | end the turn with the question and wait |
| Dispatch the roadmap writer | `spawn_agent` with `fork_turns: "none"` |
| Wait for a child | `wait_agent` (`timeout_ms` 300000–600000, wait once) |
| Invoke a skill | `$prd-<name>` |

If a capability is absent, work inline. **Never invent a tool call.**

## Instructions file

`AGENTS.md` in the project root.

## Prerequisite

Subagents require `[features] multi_agent = true` in `~/.codex/config.toml`. If it is absent,
say so once and write the roadmap inline.

## Dispatch

Omit `model` and `reasoning_effort` so the child inherits the host defaults; never guess a model
name.
