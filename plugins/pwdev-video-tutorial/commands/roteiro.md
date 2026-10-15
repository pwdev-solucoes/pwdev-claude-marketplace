---
description: Escreve o roteiro com storytelling de um vídeo do roadmap
argument-hint: "[id ou título do vídeo]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-video-tutorial:roteiro

Route this request exclusively to the portable `vtut-roteiro` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/vtut-roteiro/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
