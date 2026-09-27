# Hermes Agent Tool Mapping

| Action skills request | Hermes tool |
|---|---|
| Read a file | `read_file` |
| Create a new file | `write_file` |
| Edit a file | `patch` |
| Run a shell command | `terminal` |
| Search file contents | `search_files` |
| Find files by name | `terminal` with `find` |
| Ask the human | end the turn with the question and wait |
| Dispatch the roadmap writer | `delegate_task(goal=..., context=..., toolsets=[...], role="leaf")` |
| Invoke a skill | `skill_view("pwdev-prd:prd-<name>")` |

## Instructions file

`AGENTS.md` in the project root, or `~/.hermes/SOUL.md` globally. Read them; never edit
`SOUL.md`.

## Invoking a skill

If a namespaced `skill_view` returns "not found", read the SKILL.md directly — the bootstrap
prints the absolute skills directory for this fallback.

## Dispatch

Context is explicit in `context=`: pass the full dispatch block. The roadmap writer needs file
and terminal toolsets. If `delegate_task` is unavailable, write the roadmap inline. Do not pass
a model parameter. There is no documented wait primitive: wait in bounded 5–10 minute stretches
with a one-line status between them.

## Session limits

The bootstrap is injected on the first turn only. If skills stop triggering after compaction,
start a fresh session.
