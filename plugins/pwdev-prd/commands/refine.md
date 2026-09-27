---
description: Update an existing PRD through targeted questions about specific sections.
argument-hint: "[prd-slug]"
---

# /pwdev-prd:refine

Route this request exclusively to the portable `prd-refine` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/prd-refine/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
