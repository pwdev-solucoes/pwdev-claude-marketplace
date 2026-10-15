---
description: Gera ativo por IA — triagem, prompt, estimativa, confirmação, geração e curadoria
argument-hint: "[descrição do ativo]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# /pwdev-social-media:gerar

Route this request exclusively to the portable `social-imagem` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/social-imagem/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
