---
description: Decompose an approved PRD into an executable roadmap with an explicit dependency chain, waves, and critical path.
argument-hint: "[prd-slug]"
---

# /pwdev-prd:roadmap

Route this request exclusively to the portable `prd-roadmap` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/prd-roadmap/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
