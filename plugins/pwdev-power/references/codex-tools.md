# Codex Tool Mapping

Inspect the actual tool surface exposed in the current Codex session before acting. Tool
availability varies by host and installed plugins, so resolve each requested capability to an
available tool instead of inventing or requiring a fixed name.

| Action skills request | Typical Codex capability when exposed |
|---|---|
| Read or search files | `exec_command` with `sed`, `rg`, or another available read-only command |
| Create, replace, or edit a file | `apply_patch` |
| Run a command | `exec_command` |
| Dispatch a subagent | `spawn_agent` |
| Reach a live child again | `followup_task` |
| Wait for a child | `wait_agent` |
| List children | `list_agents` |
| Invoke a skill | `$power-<name>` |

These names are examples from the current Codex surface, not a promise that every host exposes
all of them. If a capability is absent, work inline or use another exposed equivalent. **Never
invent a tool call.**

## Instructions file

`AGENTS.md` in the project directory.

## Prerequisite

Subagents require `[features] multi_agent = true` in `~/.codex/config.toml`. If it is absent,
say so and work inline rather than failing repeatedly.

## Subagent dispatch

Use `fork_turns: "none"` only when a fresh, isolated context is a deliberate requirement of the
workflow and provide all required context in the prompt. Otherwise retain the surrounding context
appropriate to the task.

Omit `model` and `reasoning_effort` so the child inherits the host defaults unless the user,
repository governance, configuration, or an approved routing profile explicitly requires an
override. When overriding, inspect the models and effort levels exposed by the host and pass only
a supported combination; do not guess either value.

## Fix rounds

For fix rounds 1 through 3, use `followup_task` to hand the finding back to the child that
already has the context. It also revives an evicted child. Do not spawn a fresh implementer
believing you cannot talk to a live one — you can.

## Waiting

`wait_agent` is an event subscription. Use `timeout_ms` between 300000 and 600000 and wait
once. Stacking short waits that expire is not progress; it is polling with extra steps.

## Sandbox and branches

If the sandbox blocks branch creation or push — typically a detached HEAD in an externally
managed worktree — commit everything and tell the human to use the app's own branch or
hand-off control. Do not fight the sandbox.
