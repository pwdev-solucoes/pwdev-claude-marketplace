---
description: Launch, inspect, or tear down an isolated SDD Composy fleet
argument-hint: "<launch|status|teardown> [arguments]"
---

# /sdd-composy:fleet

Route this request exclusively to the portable `$sdd-fleet` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/sdd-fleet/SKILL.md`, discover the current
repository and approved task contracts, pass through `$ARGUMENTS`, and return
the shared skill result unchanged.

The adapter must not create provider command vectors, read `.env.fleet`, merge
branches, or let cmux own lifecycle truth. Supported operations are `launch`,
`status`, and `teardown`.
