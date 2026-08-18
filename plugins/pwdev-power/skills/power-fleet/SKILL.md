---
name: power-fleet
description: Use when approved phases should run unattended in parallel, when fleet status is requested, or when a fleet member must be stopped or merged
---

# Operate a Fleet

Read [fleet](../../references/fleet.md), [cmux](../../references/cmux.md),
[safety](../../references/safety.md), and [artifacts](../../references/artifacts.md) before
acting.

## Routes

| Route | Meaning |
|---|---|
| `<slug...>` | launch one or more approved phases |
| `<slug...> --via-kanban` | launch through the Hermes Kanban board — see [kanban](../../references/kanban.md) |
| `--status` | one-shot dashboard |
| `--teardown <slug> [--merge]` | stop one member |
| `--teardown --all` | stop every validated member, one call each |

Pass `--merge` only when the human explicitly asks for it.

## Launch

1. Inspect repository status and confirm a named current branch. Read `config.json` and the
   requested `spec.md` and `plan.md`. **Never read a generated fleet environment file.**
2. Resolve scripts from this installed skill at `../../scripts/`. Call only the packaged fleet
   scripts; never assemble a provider command yourself.
3. **Use the launcher of the runtime you are, and never another.** The runtime is fixed by that
   choice, recorded in the member, and refused by a runner bound to a different one. There is
   no default and no override.

   | You are | Launcher | Vector |
   |---|---|---|
   | Claude Code | `claude-fleet-up.sh` | `claude -p --dangerously-skip-permissions --no-session-persistence --output-format json <prompt>` |
   | Codex | `codex-fleet-up.sh` | `codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral --cd <worktree> --output-schema <schema> --output-last-message <file> <prompt>` |
   | Hermes | `hermes-fleet-up.sh` | `hermes -z <prompt> --in <worktree> --yolo --accept-hooks` |

4. **Before the first launch, display your runtime's exact command shape and require explicit
   acknowledgement of its dangerous flag** — `--dangerously-skip-permissions`,
   `--dangerously-bypass-approvals-and-sandbox`, or `--yolo`. No acknowledgement, no launch.
   Reject any configured `permission_mode` other than `danger-full-access`.
5. For several slugs, compare their specs and plans for repeated repository paths. Emit an
   advisory overlap warning naming the paths and let the human decide. Do not block
   automatically — plausible overlap is common and only the human knows if it matters here.
6. Invoke your launcher once per acknowledged slug. Stop launching after any failure and report
   the recovery state rather than pressing on with a partial fleet.

The launcher owns provisioning; the runner owns the lifecycle. Neither is yours to reimplement.

## Status

Invoke `fleet-dashboard.sh --once` and report each slug with its runtime, stage, status, ports,
branch, and a short message.

**Do not load or reproduce fleet logs, prompts, or result payloads**, and do not print absolute
worktree paths. If someone needs a log, give them the path to read, not its contents.

## Teardown

`fleet-teardown.sh <slug>` stops the stack, closes the member's cmux workspace, and removes the
member record, **preserving the branch and the worktree**. That default is deliberate: a fleet
member that failed is evidence.

`--merge` is refused for any member that is not `DONE`, and re-validates the terminal status
before merging. The database volume is always kept and reported.

For `--teardown --all`, enumerate validated `fleet/<slug>.json` entries and call the script once
per slug. Never hand it a glob.

## When something is wrong

| Symptom | Meaning |
|---|---|
| `cmux: no socket` | cmux is not running. Say so; do not proceed without it. |
| `registered fleet member does not match…` | you are the wrong runtime for this member, or the worktree moved. |
| `approved fleet contracts changed…` | someone edited the spec or plan mid-flight. The member is stopped on purpose. |
| A retained runner lock | a provider process group could not be proven gone. A human must look before relaunching. |
| `invalid structured result` | the provider answered with prose. The raw result is preserved next to the member's results for inspection. |

None of these are retried by re-running the launcher. Resolve the cause first.
