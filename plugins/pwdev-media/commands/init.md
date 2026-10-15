---
description: Instala a CLI pwdev-media, guarda chaves no Keychain e testa os provedores
argument-hint: "[provedor]"
allowed-tools: Bash, Read, Write, Edit
---

# /pwdev-media:init

Route this request exclusively to the portable `media-setup` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/media-setup/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
