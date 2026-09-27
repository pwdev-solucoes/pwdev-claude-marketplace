---
description: Publish an approved PRD roadmap to GitHub — Project from a template, issues, sub-issues, and blocked-by dependencies (via pwdev-github).
argument-hint: "[prd-slug]"
---

# /pwdev-prd:publish

Route this request exclusively to the portable `prd-publish` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/prd-publish/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
