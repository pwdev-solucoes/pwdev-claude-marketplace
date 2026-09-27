---
description: Deliver a GitHub issue end to end — plan, execute, review, at most 2 fix cycles, then a pull request that closes it. Never merges.
argument-hint: "[#issue | issue URL] [--base <ref>]"
---

# /pwdev-feat:loop

Route this request exclusively to the portable `feat-loop` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/feat-loop/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS`. Paths `references/`, `scripts/`, `templates/` and `schemas/` in the skill are
relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
