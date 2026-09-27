# Codex Tool Mapping

Inspect the tool surface actually exposed in the session. Resolve each capability to an
available tool instead of requiring a fixed name.

| Action skills request | Typical Codex capability |
|---|---|
| Read or search files | `exec_command` with `sed`, `rg`, or another read-only command |
| Create, replace, or edit a file | `apply_patch` |
| Run a command | `exec_command` |
| Ask the human | end the turn with the question and wait |
| Dispatch a subagent | `spawn_agent` |
| Reach a live child again | `followup_task` |
| Wait for a child | `wait_agent` |
| Invoke a skill | `$feat-<name>` |

If a capability is absent, work inline. **Never invent a tool call.**

## Instructions file

`AGENTS.md` in the project root.

## Prerequisite

Subagents require `[features] multi_agent = true` in `~/.codex/config.toml`. If it is absent,
say so once and run the executor contract inline.

## Dispatch

Use `fork_turns: "none"` for the executor and the advisor: both are deliberately fresh and get
everything in the dispatch prompt. Omit `model` and `reasoning_effort` so the child inherits the
host defaults unless `.planning/config.json` carries an explicit override that names a model the
host exposes; never guess a model name.

`wait_agent` is an event subscription: `timeout_ms` between 300000 and 600000, wait once.

## Sandbox

If the sandbox blocks the commit (for example a detached HEAD in a managed worktree), leave the
changes staged, report it in the status, and let the human commit.
