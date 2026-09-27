---
description: Cria um GitHub Project a partir de um template (preset do plugin ou Project-modelo), com personalização antes de criar
argument-hint: "[nome do project]"
allowed-tools: Bash, Read, Write
---

# /pwdev-github:project

Route this request exclusively to the portable `github-project` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/github-project/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
