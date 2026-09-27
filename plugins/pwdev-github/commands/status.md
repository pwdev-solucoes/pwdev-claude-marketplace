---
description: Estado do plugin — gh, scopes, repo, Project ativo e roadmaps publicados
allowed-tools: Bash, Read
disable-model-invocation: true
---

# /pwdev-github:status

Route this request exclusively to the portable `github-status` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/github-status/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
