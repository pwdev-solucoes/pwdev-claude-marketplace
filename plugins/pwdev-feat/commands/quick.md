---
description: Quick task — no plan file, direct execution for simple tasks (bugfix, config, rename, 1-5 files).
argument-hint: "[task description]"
---

# /pwdev-feat:quick

Route this request exclusively to the portable `feat-quick` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/feat-quick/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS`. Paths `references/`, `scripts/`, `templates/` and `schemas/` in the skill are
relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
