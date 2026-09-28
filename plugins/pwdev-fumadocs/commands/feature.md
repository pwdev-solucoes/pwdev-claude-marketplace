---
description: Adiciona uma feature ao Fumadocs — busca, llms.txt, MCP, OG, OpenAPI, i18n, export estático
argument-hint: "[pedido ou caminho do app]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch
---

# /pwdev-fumadocs:feature

Route this request exclusively to the portable `fumadocs-feature` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/fumadocs-feature/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/` and `scripts/` in
the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
