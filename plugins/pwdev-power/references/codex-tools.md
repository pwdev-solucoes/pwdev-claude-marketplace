# Codex Tool Mapping

| Action skills request | Codex tool |
|---|---|
| Read a file | `read_file` |
| Create or replace a file | `write_file` |
| Edit a file | `apply_patch` |
| Run a shell command | `shell` |
| Search file contents | `shell` with `rg` |
| Dispatch a subagent | `spawn_agent` |
| Reach a live child again | `followup_task` |
| Wait for a child | `wait_agent` |
| List children | `list_agents` |
| Invoke a skill | `$power-<name>` |

## Instructions file

`AGENTS.md` in the project directory.

## Prerequisite

Subagents require `[features] multi_agent = true` in `~/.codex/config.toml`. If it is absent,
say so and work inline rather than failing repeatedly.

## Subagent dispatch

Always pass `fork_turns: "none"`. The default `"all"` copies the whole transcript into the
child, which is the opposite of a fresh context and is the single most expensive mistake
available here.

Always set **both** `model` and `reasoning_effort`. Setting only `model` resets effort to that
model's default, which silently downgrades a task you meant to route upward. A backstop in
`~/.codex/config.toml` under `[agents]` (`default_subagent_model`,
`default_subagent_reasoning_effort`) is worth having, but does not excuse omitting them.

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
