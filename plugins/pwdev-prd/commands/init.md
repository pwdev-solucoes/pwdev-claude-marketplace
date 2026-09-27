---
description: Initialize the pwdev-prd framework — creates .planning/prds/ workspace.
---

# /pwdev-prd:init

Route this request exclusively to the portable `prd-init` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/prd-init/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
