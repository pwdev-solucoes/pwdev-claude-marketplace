---
description: Query the audit trail database for events, decisions, artifacts, and statistics. Export a Markdown/PDF report.
argument-hint: "[summary | events | decisions | artifacts | stats | export | query <SQL>]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

# /pwdev-feat:audit

Route this request exclusively to the portable `feat-audit` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/feat-audit/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS`. Paths `references/`, `scripts/`, `templates/` and `schemas/` in the skill are
relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
