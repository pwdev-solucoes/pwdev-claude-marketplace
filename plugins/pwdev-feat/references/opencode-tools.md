# OpenCode Tool Mapping

| Action skills request | OpenCode tool |
|---|---|
| Read a file | `read` |
| Create or edit a file | `edit` or `write` |
| Run a command | `bash` |
| Search file content | `grep` |
| Find files by pattern | `glob` |
| Ask the human | end the turn with the question and wait |
| Dispatch a subagent | `task` with the full dispatch prompt as context |
| Invoke a skill | load `feat-<name>` with the `skill` tool, or `/feat-<name>` |

## Installation

OpenCode has no plugin manifest. `.opencode-plugin/install.py` links each `skills/feat-*`
folder into `~/.config/opencode/skills/` (or `<project>/.opencode/skills/` with `--project`) and
writes one `command/feat-<name>.md` per Claude command, so `/feat-<name>` routes to the same
skill. It never copies (plugin-relative paths resolve through the symlink) and never touches
`opencode.json`.

## Instructions file

`AGENTS.md` in the project root.

## Dispatch

If `task` is unavailable, run the contract inline. Do not pass a model parameter unless the
project config names one explicitly.
