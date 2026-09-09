---
description: Independently verify a SDD Composy task and request its guarded lifecycle transition
argument-hint: "<TASK-ID> [context]"
---

# /sdd-composy:verify

Route this request exclusively to the portable `$sdd-verify` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/sdd-verify/SKILL.md`, pass through `$ARGUMENTS`
and the current repository context, and return the shared skill's result
unchanged. The shared task engine owns artifact predicates and lifecycle
transitions. These lifecycle transitions are guarded; this adapter must not
infer approval or complete a task directly.
