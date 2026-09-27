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
| Dispatch the roadmap writer | `Agent` with `subagent_type: "pwdev-prd:roadmap"` |
| Invoke a skill | the `Skill` tool, or the `/pwdev-prd:<cmd>` wrapper |

## Instructions file

`CLAUDE.md` in the project root.

## Hooks

`hooks/hooks.json` records the audit trail mechanically (session, subagent start/stop with
duration, `.planning/` writes) and blocks secret reads with `scripts/guard-secrets.sh`. Both are
Claude-only.
