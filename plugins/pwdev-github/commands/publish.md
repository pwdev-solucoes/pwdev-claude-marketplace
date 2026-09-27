---
description: Publica um roadmap pwdev-roadmap/1 no GitHub — issues, sub-issues, milestones, blocked-by e campos do Project, idempotente e retomável
argument-hint: "<caminho/roadmap.json>"
allowed-tools: Bash, Read, Write
---

# /pwdev-github:publish

Route this request exclusively to the portable `github-publish` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/github-publish/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
