---
description: Confere, renderiza com o portão e entrega o tutorial
argument-hint: "[ajuste]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-video-tutorial:revisar

Route this request exclusively to the portable `vtut-revisar` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/vtut-revisar/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
