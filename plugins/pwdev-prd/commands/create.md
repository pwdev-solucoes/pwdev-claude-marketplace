---
description: Start a structured interview to create a new PRD. Produces Markdown + optional JSON.
argument-hint: "[feature or system description]"
---

# /pwdev-prd:create

Route this request exclusively to the portable `prd-create` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/prd-create/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
