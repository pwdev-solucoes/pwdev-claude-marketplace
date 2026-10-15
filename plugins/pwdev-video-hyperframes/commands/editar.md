---
description: Edita um vídeo falado do começo ao fim: corte, plano, amostra, vídeo inteiro e entrega
argument-hint: "[pasta dos vídeos e pedido]"
allowed-tools: Bash, Read, Write, Edit
---

# /pwdev-video-hyperframes:editar

Route this request exclusively to the portable `vhf-editar` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/vhf-editar/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...` in the skill are relative to
`${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
