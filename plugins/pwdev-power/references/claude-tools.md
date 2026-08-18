# Claude Code Tool Mapping

| Action skills request | Claude Code tool |
|---|---|
| Read a file | `Read` |
| Create or replace a file | `Write` |
| Edit a file | `Edit` |
| Run a shell command | `Bash` |
| Search file contents | `Grep` |
| Find files by name | `Glob` |
| Fetch a URL | `WebFetch` |
| Search the web | `WebSearch` |
| Dispatch a subagent | `Task` / `Agent` with `subagent_type` |
| Task tracking | the todo tool |
| Invoke a skill | the `Skill` tool |

## Instructions file

`CLAUDE.md` in the project directory.

## Subagent dispatch

The packaged subagents in `agents/` are the dispatch targets, and they carry their own model,
tool allowlist and turn cap:

| `subagent_type` | Use for |
|---|---|
| `pwdev-power:implementer` | one plan task, end to end |
| `pwdev-power:task-reviewer` | one review package |
| `pwdev-power:verifier` | adversarial verification of a feature |
| `pwdev-power:roadmap` | decomposing an approved requirement |
| `pwdev-power:mapper` | mapping an existing repository into the context documents |

Dispatching several subagents in one message runs them concurrently. Do that only for work
that shares no state — never for implementers, which must run one at a time.

## Skill references

Load another skill through the `Skill` tool by its namespaced name, for example
`pwdev-power:power-tdd`. Do not use `@`-links to pull a skill in: they force an immediate
load and burn context you have not decided to spend.
