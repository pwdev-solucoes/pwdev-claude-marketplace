---
description: Evolve each roadmap feature with user stories — acceptance criteria (CA) and business rules (RN) — one feature at a time, up to the Definition of Ready.
argument-hint: "[prd-slug] [feature-id | next]"
---

# /pwdev-prd:stories

Route this request exclusively to the portable `prd-stories` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/prd-stories/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
