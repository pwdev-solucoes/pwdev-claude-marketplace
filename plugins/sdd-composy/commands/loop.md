---
description: Start, inspect, continue, or cancel a bounded SDD Composy loop
argument-hint: "<start|status|continue|cancel> [arguments]"
---

# /sdd-composy:loop

Route this request exclusively to the portable `$sdd-loop` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/sdd-loop/SKILL.md`, discover the current repository
and task context, pass through `$ARGUMENTS`, and return the shared skill result
unchanged. The skill must disclose the default three-iteration bound, require
explicit human approval, and safe-stop on cancellation, scope expansion,
architectural ambiguity, destructive work, no progress, or missing verification.

Supported operations are `start`, `status`, `continue`, and `cancel`; this
adapter must not create provider-specific command vectors or bypass lifecycle
guards.
