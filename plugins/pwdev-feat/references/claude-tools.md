# Claude Code Tool Mapping

| Action skills request | Claude Code tool |
|---|---|
| Read a file | `Read` |
| Create or replace a file | `Write` |
| Edit a file | `Edit` |
| Run a shell command | `Bash` |
| Search file contents | `Grep` |
| Find files by name | `Glob` |
| Ask the human | plain text, or `AskUserQuestion` when available |
| Dispatch a subagent | `Task` / `Agent` with `subagent_type` |
| Invoke a skill | the `Skill` tool, or the `/pwdev-feat:<cmd>` wrapper |

## Instructions file

`CLAUDE.md` in the project root (it may import `AGENTS.md` with `@AGENTS.md`). See
[project-files.md](project-files.md).

## Subagents

| `subagent_type` | Use for | Model key |
|---|---|---|
| `pwdev-feat:executor` | one action plan, IMPLEMENT or REPORT mode | `feat-executor` |
| `pwdev-feat:advisor` | one NEEDS_ADVICE decision | `feat-advisor` |

Always pass `model` resolved per [model-profiles.md](model-profiles.md).

## Hooks

`hooks/hooks.json` records the audit trail mechanically (session, subagent start/stop with
duration, `.planning/` writes) and blocks secret reads with `scripts/guard-secrets.sh`. Both are
Claude-only; see [safety.md](safety.md) and [audit-schema.md](audit-schema.md).
