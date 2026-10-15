---
description: Exporta peças aprovadas e monta o pacote com legendas e alt text
argument-hint: "[campanha]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-social-media:exportar

Route this request exclusively to the portable `social-entrega` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/social-entrega/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
