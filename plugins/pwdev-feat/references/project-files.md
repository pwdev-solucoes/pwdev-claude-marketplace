# Project instructions files

Each runtime reads a project instructions file from the repository root:

| Runtime | File |
|---|---|
| Claude Code | `CLAUDE.md` (may contain `@AGENTS.md` to import the shared file) |
| Codex, Hermes, OpenCode | `AGENTS.md` |

Skill bodies never write these two filenames literally — Hermes drops any skill whose body
contains them. Skills say "the project instructions file" and point here.

## Reading

Read `AGENTS.md` first, then `CLAUDE.md`; when both exist and one imports the other, read the
content once. The sections pwdev-feat relies on are **Stack**, **Commands** (lint, test, build,
e2e) and **Golden Rules**; verification commands declared there take precedence over detected
ones.

## Writing (`feat-setup` only)

- `AGENTS.md` is the canonical file generated from `templates/AGENTS.template.md`.
- If `CLAUDE.md` does not exist, create it with a single line `@AGENTS.md` so Claude Code loads
  the same rules.
- If either file already exists with content, show its first lines and ask: update (merge
  sections), replace, or skip. Never overwrite silently.
