---
description: Execute one approved SDD Composy task with guarded evidence and transitions
argument-hint: "<TASK-ID> [context]"
---

# /sdd-composy:execute

Route this request exclusively to the portable `$sdd-execute` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/sdd-execute/SKILL.md`, pass through `$ARGUMENTS`
and the current repository context, and return the shared skill's result
unchanged. The adapter does not execute commands or duplicate the policy.
