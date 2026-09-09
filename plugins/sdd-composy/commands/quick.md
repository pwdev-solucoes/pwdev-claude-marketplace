---
description: Deliver a bounded SDD Composy change with guarded escalation
argument-hint: "<objective>"
---

# /sdd-composy:quick

Route this request exclusively to the portable `$sdd-quick` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/sdd-quick/SKILL.md`, pass through `$ARGUMENTS`
and the current repository context, and return the shared skill's result
unchanged. The skill must register a normal task and escalate when its
five-file or verification boundary cannot be proven; this command never
bypasses task lifecycle guards.
