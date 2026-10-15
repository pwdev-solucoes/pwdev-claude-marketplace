---
description: Consulta o catálogo e recomenda modelo/app por categoria e objetivo
argument-hint: "[tarefa ou categoria]"
allowed-tools: Bash, Read, Write, Edit
---

# /pwdev-media:catalogo

Route this request exclusively to the portable `media-catalogo` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/media-catalogo/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
