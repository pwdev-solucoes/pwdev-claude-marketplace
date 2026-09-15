---
description: Inspect, plan, and explicitly approve SDD Composy task synchronization
argument-hint: "<inspect|plan> <markdown-root> <state> | apply <markdown-root> <state> <plan.json> --authority markdown|json --confirmation-token CONFIRM-SDD-SYNC"
---

# /sdd-composy:sync

Route this request exclusively to the portable `$sdd-sync` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/sdd-sync/SKILL.md`, pass through `$ARGUMENTS` and the
current repository context, and return the shared skill's result unchanged.
