---
description: Analyze the existing codebase — deterministic evidence scan plus architecture, conventions, testing and concerns context documents.
---

# /pwdev-feat:map-codebase

Route this request exclusively to the portable `feat-map` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/feat-map/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS`. Paths `references/`, `scripts/`, `templates/` and `schemas/` in the skill are
relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
