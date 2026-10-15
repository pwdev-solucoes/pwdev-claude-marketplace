---
description: Explora o sistema pelo código e pela navegação real e escreve o mapa
argument-hint: "[url do sistema] [pasta do código]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-video-tutorial:explorar

Route this request exclusively to the portable `vtut-explorar` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/vtut-explorar/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
