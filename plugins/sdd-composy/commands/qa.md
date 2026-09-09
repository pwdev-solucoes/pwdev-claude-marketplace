---
description: Run independent quality assurance for an SDD Composy task
argument-hint: "<TASK-ID> [context]"
---

# /sdd-composy:qa

Route this request exclusively to the portable `$sdd-qa` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/sdd-qa/SKILL.md`, pass through `$ARGUMENTS`
and the current repository context, and return the shared skill's result unchanged.
