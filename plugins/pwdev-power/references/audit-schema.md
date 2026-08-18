# Audit

Opt-in. Enabled only when `config.json` has `"audit": true` **and** `sqlite3` is available
**and** `.planning/power/audit/pwdev-audit.db` already exists. Audit is best-effort by
construction: a failure warns and never changes, rolls back, or replaces the lifecycle result
it was describing.

## Two paths, one schema

`scripts/audit-log.sh` is called **explicitly by the skills**. It is the portable path and
works on all three runtimes. `hooks/hooks.json` adds automatic session, subagent and artifact
events on Claude only. The hooks enrich the trail; nothing depends on them.

## Commands

```text
audit-log.sh event    <command> <phase> <action> [target] [detail]
audit-log.sh spawn    <command> <phase> <role> <tier> [detail]
audit-log.sh decision <phase> <decision> [rationale] [alternatives]
audit-log.sh gate     <phase> <APPROVED|REJECTED|BLOCKED> [target]
```

## Allowed actions

`started`, `completed`, `failed`, `gate_approved`, `gate_rejected`, `gate_blocked`,
`artifact_written`, `decision_recorded`, `ruling_recorded`, `task_dispatched`,
`task_reviewed`, `fix_round`, `verify_verdict`, `fleet_launched`, `fleet_stage`,
`fleet_teardown`, `kanban_bridged`.

An unknown action is rejected before the write, not coerced into a neighbour.

## Record only after the durable fact

`fleet_launched` follows a successful launch, not the intent to launch. `fleet_stage` follows
the atomic status publication. `verify_verdict` follows the written verdict. An audit trail
that records intentions is a trail of things that may not have happened.

## Secret filter

Reject, before appending: any unknown action, invalid JSON, any secret-like key, any direct or
nested key whose name contains `model` or `prompt`, and any secret-like target. Model names
and prompts are exactly the fields most likely to carry both cost signal and user content, so
they never enter the trail — `spawn` records a *tier*, not a model name.

Targets are recorded relative to the repository root. Absolute paths, worktree paths, raw
provider output and result payloads never enter the trail.

## Integrity

Never repair an invalid trail automatically. Preserve it, report the exact errors, and require
explicit direction before any corrective copy or replacement.
