---
description: Confere se o editor de vídeo está pronto (sem instalar nada)
argument-hint: ""
allowed-tools: Bash, Read, Write, Edit
---

# /pwdev-video-hyperframes:status

Route this request exclusively to the portable `vhf-setup` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/vhf-setup/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments (status: check only, install nothing). Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
