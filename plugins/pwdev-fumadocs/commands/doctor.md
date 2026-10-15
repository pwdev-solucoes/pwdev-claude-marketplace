---
description: Diagnostica erros e o estado do Fumadocs no projeto; corrige só após aprovação
argument-hint: "[pedido ou caminho do app]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch
---

# /pwdev-fumadocs:doctor

Route this request exclusively to the portable `fumadocs-doctor` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/fumadocs-doctor/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/` and `scripts/` in
the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
