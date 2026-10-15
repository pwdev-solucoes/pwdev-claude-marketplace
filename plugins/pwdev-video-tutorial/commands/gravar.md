---
description: Grava a tela executando o roteiro no sistema real
argument-hint: "[id do vídeo]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-video-tutorial:gravar

Route this request exclusively to the portable `vtut-gravar` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/vtut-gravar/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
