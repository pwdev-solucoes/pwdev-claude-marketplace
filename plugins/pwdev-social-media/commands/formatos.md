---
description: Formatos e zonas seguras; deriva uma peça em todos os formatos
argument-hint: "[formato ou peça]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-social-media:formatos

Route this request exclusively to the portable `social-formatos` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/social-formatos/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
