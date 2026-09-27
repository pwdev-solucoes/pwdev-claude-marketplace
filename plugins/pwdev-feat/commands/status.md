---
description: Show current features — pending, executed, with caveats, failed, resumable — and codebase context health.
disable-model-invocation: true
allowed-tools: Read, Bash
---

# /pwdev-feat:status

Route this request exclusively to the portable `feat-status` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/feat-status/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS`. Paths `references/`, `scripts/`, `templates/` and `schemas/` in the skill are
relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
