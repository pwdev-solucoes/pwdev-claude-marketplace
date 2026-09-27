---
description: Export a PRD as a GitHub issue or regenerate the JSON export.
argument-hint: "[prd-slug] [--json | --github]"
---

# /pwdev-prd:export

Route this request exclusively to the portable `prd-export` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/prd-export/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
