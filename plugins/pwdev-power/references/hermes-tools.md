# Hermes Agent Tool Mapping

| Action skills request | Hermes tool |
|---|---|
| Read a file | `read_file` |
| Create a new file | `write_file` |
| Edit a file (targeted patch) | `patch` |
| Run a shell command | `terminal` |
| Search file contents | `search_files` |
| Find files by name | `terminal` with `find` |
| Fetch a URL | `web_extract(urls=[...])` |
| Search the web | `web_search(query=...)` |
| Dispatch a subagent | `delegate_task(goal=..., context=..., toolsets=[...], role="leaf")` |
| Task tracking | the `todo` tool; `hermes kanban` CLI for multi-agent boards |
| Invoke a skill | `skill_view("pwdev-power:power-<name>")` |

## Instructions file

`AGENTS.md` in the project directory, or `SOUL.md` globally at `~/.hermes/SOUL.md`. Read them;
never edit them.

## Invoking a skill

The `skills` toolset exposes `skill_view` and `skills_list`. If a namespaced lookup returns
"not found", read the file directly instead — the bootstrap prints the absolute skills
directory for exactly this fallback.

## Subagent dispatch

Context is passed explicitly in `context=`; there is no transcript fork. That matches this
plugin's rule already: hand the child its brief path and the interfaces it needs, never
accumulated history.

Grant capability through `toolsets=[...]`. An implementer needs file and shell access; a
reviewer needs read and search only. If `delegate_task` is unavailable, do the work inline
rather than inventing a tool call.

## Two documented gaps

**Per-dispatch model selection is not established for `delegate_task`.** If it accepts model
or provider parameters, set them and record what worked here. If it does not, either route the
work through `hermes kanban create --model/--provider`, which does take a per-task override,
or run inline. Never invent a parameter to satisfy the rule that models be explicit.

**There is no documented `wait_agent` equivalent.** So: while you have local work, do it. When
idle, wait in bounded 5–10 minute stretches with a one-line status between them, and
reconcile what came back. Never poll in a tight loop, never wait silently forever.

## Session limits

The bootstrap is injected on the first turn only, and Hermes has no post-compaction hook. A
long session that compacts over its first turn loses it. If skills stop triggering, start a
fresh session — that is the fix, and it is not a bug you can patch from inside the plugin.
