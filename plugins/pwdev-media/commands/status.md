---
description: Estado do pwdev-media: ferramentas, chaves (teste ao vivo), catálogo e gasto do mês
argument-hint: ""
allowed-tools: Bash, Read, Write, Edit
---

# /pwdev-media:status

Route this request exclusively to the portable `media-setup` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/media-setup/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments (this command asks for the status step only). Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
