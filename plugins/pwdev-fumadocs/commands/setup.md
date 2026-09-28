---
description: Cria um site Fumadocs ou adiciona Fumadocs a um app existente, com verificação
argument-hint: "[pedido ou caminho do app]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch
---

# /pwdev-fumadocs:setup

Route this request exclusively to the portable `fumadocs-setup` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/fumadocs-setup/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/` and `scripts/` in
the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
