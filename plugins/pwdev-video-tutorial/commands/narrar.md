---
description: Gera a narração por cena (voz local grátis, sua voz ou ElevenLabs)
argument-hint: "[voz]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-video-tutorial:narrar

Route this request exclusively to the portable `vtut-narrar` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/vtut-narrar/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
