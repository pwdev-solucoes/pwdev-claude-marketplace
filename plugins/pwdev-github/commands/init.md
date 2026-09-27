---
description: Setup do GitHub — verifica gh, autenticação e scopes, define owner/repo padrão e o Project ativo
argument-hint: "[owner/repo]"
allowed-tools: Bash, Read, Write, Edit
---

# /pwdev-github:init

Route this request exclusively to the portable `github-init` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/github-init/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
