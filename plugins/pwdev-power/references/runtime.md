# Runtimes

This plugin ships one set of skills and three thin adapters. The skills are the single source
of truth; an adapter only decides how the skill is entered and which tool names its actions
resolve to.

| | Claude Code | Codex | Hermes Agent |
|---|---|---|---|
| Entry point | `commands/<name>.md` | `skills/<name>/agents/openai.yaml` | `.hermes-plugin/` registration |
| Invocation | `/pwdev-power:<cap>` | `$power-<cap>` | `skill_view("pwdev-power:power-<cap>")` |
| Manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.hermes-plugin/plugin.yaml` |
| Bootstrap | `SessionStart` hook | native skill discovery | `pre_llm_call`, first turn |
| Tool mapping | [claude-tools.md](claude-tools.md) | [codex-tools.md](codex-tools.md) | [hermes-tools.md](hermes-tools.md) |

Read the mapping for the runtime you are before dispatching anything.

## Identify yourself once

You are exactly one runtime for the whole session. Decide which from your own tool surface,
not from `config.json` — that field records who initialized the workspace, not who is running
now. Then use only that runtime's launcher and tool names.

## Subagent dispatch, in one line each

- **Claude**: the `Task`/`Agent` tool with a declared `subagent_type` from `agents/`.
- **Codex**: `spawn_agent` with `fork_turns: "none"`. The default `"all"` copies the entire
  transcript into the child, which defeats the whole point of a fresh context.
- **Hermes**: `delegate_task(goal=..., context=..., toolsets=[...], role="leaf")`. Context is
  explicit; there is no transcript fork to suppress.

If a runtime has no subagent mechanism available, do the work inline. **Never invent a tool
call.**

## Model selection

Always name the model explicitly when dispatching. Omitting it inherits the session's model,
which is usually the most expensive one. See [model-profiles.md](model-profiles.md) for the
routing table, and the per-runtime mapping for how to express it — including what to do on
Hermes, where per-dispatch model selection is not documented.

## Waiting for children

Never poll in a tight loop, and never wait silently forever. While you still have local work,
do it. When you are genuinely idle, wait in bounded stretches and print a one-line status
between them. On Codex, `wait_agent` is an event subscription, not a poll: give it a
`timeout_ms` of 300000–600000 and wait once rather than eight times.
