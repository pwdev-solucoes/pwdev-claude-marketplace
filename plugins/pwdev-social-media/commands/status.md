---
description: Mostra o estado — contexto, núcleo pwdev-media, chaves, conectores e gasto do mês
argument-hint: ""
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-social-media:status

Route this request exclusively to the portable `social-contexto` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/social-contexto/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments (status: report only, change nothing). Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
