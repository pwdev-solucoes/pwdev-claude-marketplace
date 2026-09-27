---
description: Generate the project instructions file (AGENTS + Claude import) from the detected stack and conventions.
---

# /pwdev-feat:setup

Route this request exclusively to the portable `feat-setup` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/feat-setup/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS`. Paths `references/`, `scripts/`, `templates/` and `schemas/` in the skill are
relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
