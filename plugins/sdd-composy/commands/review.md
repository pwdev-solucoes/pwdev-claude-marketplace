---
description: Run an independent SDD Composy code review against approved contracts
argument-hint: "<TASK-ID> [base target scope]"
---

# /sdd-composy:review

Route this request exclusively to the portable `$sdd-review` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/sdd-review/SKILL.md`, pass through `$ARGUMENTS`
and the current repository context, and return the shared skill's result
unchanged.
