---
description: Roteiro, storyboard e prompts de vídeo; gera pelo Runway com confirmação separada
argument-hint: "[duração] [tema]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-social-media:video

Route this request exclusively to the portable `social-video` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/social-video/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
