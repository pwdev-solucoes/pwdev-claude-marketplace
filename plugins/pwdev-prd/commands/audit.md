---
description: Query the audit trail database for events, decisions, artifacts, and statistics. Export full PDF report.
argument-hint: "[summary | events | decisions | artifacts | stats | export | query <SQL>]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

# /pwdev-prd:audit

Route this request exclusively to the portable `prd-audit` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/prd-audit/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS` as the arguments. Paths `<plugin-root>/...`, `references/`, `scripts/` and
`templates/` in the skill are relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
