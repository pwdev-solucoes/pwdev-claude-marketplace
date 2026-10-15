---
description: Monta o vídeo final com legenda e zoom no clique, e o tutorial em texto
argument-hint: "[id do vídeo]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-video-tutorial:montar

Route this request exclusively to the portable `vtut-montar` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/vtut-montar/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
