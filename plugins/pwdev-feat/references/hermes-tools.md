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
| Dispatch a subagent | `delegate_task(goal=..., context=..., toolsets=[...], role="leaf")` |
| Invoke a skill | `skill_view("pwdev-feat:feat-<name>")` |

## Instructions file

`AGENTS.md` in the project root, or `~/.hermes/SOUL.md` globally. Read them; never edit
`SOUL.md`.

## Invoking a skill

If a namespaced `skill_view` returns "not found", read the SKILL.md directly — the bootstrap
prints the absolute skills directory for this fallback.

## Dispatch

Context is explicit in `context=`: pass the full dispatch prompt. The executor needs file and
shell toolsets; the advisor needs read, search and shell only. If `delegate_task` is unavailable,
run the contract inline.

Per-dispatch model selection is not established for `delegate_task`: do not pass a model
parameter; record the host model in the audit as `inherited`.

There is no documented wait primitive: while waiting, work in bounded 5–10 minute stretches with
a one-line status between them.

## Session limits

The bootstrap is injected on the first turn only. If skills stop triggering after compaction,
start a fresh session.
