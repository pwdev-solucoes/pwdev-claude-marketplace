# Kanban bridge

`--via-kanban` is an alternative to running the fleet's own runner: approved phases become
tasks on the Hermes Kanban board, and the Hermes dispatcher executes them. The board is a
durable SQLite task graph with atomic claims, dependencies, and execution by a named profile
in an isolated workspace — an orchestrator this plugin should use rather than duplicate.

Available only when the `hermes` CLI is present. It is never the default.

## Mapping

| pwdev-power | `hermes kanban` |
|---|---|
| Approved phase | `create "<title>" --workspace worktree:<path>` (or `--project <slug>`) |
| Member branch | `--branch power-fleet/<slug>` |
| Capability to run | `--skill power-execute` |
| Relaunch idempotency | `--idempotency-key power-<slug>-<spec_sha7>` |
| Correction cap | `--max-retries 2` |
| Member timeout | `--max-runtime 2h` |
| Model routing | `--model` / `--provider` |
| Dependencies | `--parent <id>` (repeatable), `kanban link <parent> <child>` |
| Human gate | `request-review`, `request-changes`, `promote` |
| Reading state | `kanban list --json`, `kanban show <id> --json` |
| Executing | `kanban dispatch` (add `--dry-run --json` to preview), `kanban daemon` |

The idempotency key embeds the spec hash on purpose: relaunching the same approved phase
returns the same task instead of duplicating it, while an edited spec produces a different key
and therefore a genuinely new task. That is the same property the member hashes give the
native runner, expressed in the board's own vocabulary.

## What changes owner

This is the part that must be understood before choosing this route.

| Concern | Native runner | Via Kanban |
|---|---|---|
| Correction cap | the runner's own two-cycle loop | `--max-retries` plus dispatcher `--failure-limit` |
| Human gate | acknowledgement at launch | `request-review` / `request-changes` on the card |
| Process ownership | this plugin's process group discipline | the dispatcher's SIGTERM→SIGKILL and re-queue |
| Stage sequencing | `plan → execute → review → verify` in one runner | task dependencies on the board |

What does **not** change owner: the contract hashes. Record `spec_sha256` and `plan_sha256` in
the member record alongside the task id, and re-check them before accepting a result. That is
what stops a spec edited mid-flight from passing as approved, and the board has no opinion
about it.

## State mirroring

`scripts/kanban-bridge.sh` translates one way and mirrors the other. It reads `kanban list
--json` and reflects each card into cmux: `set-status` for the current step, `set-progress`
across the phase's cards, `workspace-action --action set-color` for terminal states, and
`notify` when a card enters `review` or `blocked`.

Board states are `triage`, `todo`, `ready`, `running`, `review`, `blocked`, `done`,
`scheduled`, `archived`. Map them to member status as: `running` → `RUNNING`, `done` → `DONE`,
`blocked` and `review` → `NEEDS_HUMAN`, everything else → `ACTIVE`.

## Swarm

`kanban swarm --worker PROFILE:TITLE[:SKILL] --verifier <profile> --synthesizer <profile>`
builds a graph of parallel workers feeding a verifier and then a synthesizer. That is the exact
shape of this plugin's review-and-verify phase, so use `swarm` for it on this route instead of
assembling the graph card by card.

## Preflight

Before bridging: `hermes kanban init` is idempotent and safe to run. Check that the cmux hook
integration is installed; if it is not, print `cmux hooks hermes-agent install` and let the
human run it. **Never install it yourself** — it writes the human's configuration.

Always preview with `kanban dispatch --dry-run --json` and show the human what would spawn
before anything spawns.
