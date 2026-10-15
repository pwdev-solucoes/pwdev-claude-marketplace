---
description: Confere se o editor com Remotion está pronto (sem instalar nada)
argument-hint: ""
allowed-tools: Bash, Read, Write, Edit
---

# /pwdev-video-remotion:status

Route this request exclusively to the portable `vrm-setup` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/vrm-setup/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments (status: check only, install nothing). Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
