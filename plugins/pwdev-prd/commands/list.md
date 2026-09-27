---
description: List all PRDs in the workspace with status summary.
disable-model-invocation: true
allowed-tools: Read, Bash
---

# /pwdev-prd:list

Route this request exclusively to the portable `prd-list` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/prd-list/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
