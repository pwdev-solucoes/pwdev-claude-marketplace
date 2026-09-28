---
description: Escreve, organiza ou migra páginas, meta.json e navegação do Fumadocs
argument-hint: "[pedido ou caminho do app]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch
---

# /pwdev-fumadocs:content

Route this request exclusively to the portable `fumadocs-content` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/fumadocs-content/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/` and `scripts/` in
the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
