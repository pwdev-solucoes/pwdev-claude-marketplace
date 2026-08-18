# PWDEV Power

Disciplined spec-driven development that runs on **Claude Code, Codex, and Hermes Agent**, with
isolated autonomous fleets on **cmux**.

Fast like a lightweight feature planner, with the product layer of a heavyweight one, and the
engineering disciplines that neither usually carries: a brainstorming gate before any code, plans
whose constraints travel verbatim to the engineer who implements them, execution with a durable
ledger and a bounded fix loop, and verification that tries to refute completion rather than
confirm it.

## Install

```bash
# Claude Code
/plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
/plugin install pwdev-power

# Hermes Agent
hermes plugins install pwdev-solucoes/pwdev-claude-marketplace --enable
# or, for repo-local skills in a checkout:
hermes skills trust .
```

Codex discovers the skills from `.codex-plugin/plugin.json`; invoke them as `$power-<name>`.

## The cycle

```text
/pwdev-power:init                  set up the workspace, report the runtime surface
/pwdev-power:product prd           interview, then an approved requirement
/pwdev-power:product roadmap       Phase → Epic → Feature → Task, with traceability
/pwdev-power:plan <feature>        brainstorm → spec → executable plan
/pwdev-power:exec <slug>           task by task, with review between tasks
/pwdev-power:verify <slug>         adversarial verification, then integration
/pwdev-power:quick <task>          a bounded change, no plan file
/pwdev-power:fleet <slugs>         approved phases, unattended and in parallel
```

Nothing crosses a gate without a human. Approval is recorded, never inferred.

## What it is built on

Fourteen skills, four subagents, and twelve reference contracts. The skills are the single source
of truth; each runtime gets a thin adapter and nothing else.

| Skill | Triggers on |
|---|---|
| `power` | session start — how to find and apply the rest |
| `power-brainstorm` | any new behaviour, before design |
| `power-plan` | a design that needs decomposing |
| `power-execute` | an approved plan that needs running |
| `power-tdd` | writing any implementation code |
| `power-debug` | a bug, failure, or surprise |
| `power-verify` | any claim that something works |
| `power-review` | requesting or receiving review |
| `power-product` | a requirement or a roadmap |
| `power-quick` | a small, understood change |
| `power-worktree` | starting isolated work |
| `power-finish` | complete and green |
| `power-fleet` | parallel unattended phases |
| `power-init` | a repository with no workspace yet |

## Three rules that survive every rationalization

1. **No production code without a failing test first**, and the red must be observed.
2. **No fix without root cause investigation first**; three failed fixes means the architecture
   is the suspect.
3. **No success claim without running the command and reading its output.**

## The fleet

One approved phase, one Git worktree, one Docker stack, one cmux workspace. Ports are allocated
from the first free slot, published only on loopback, and the generated environment file is
written under `umask 077` and kept out of the branch.

The privileged provider command exists in exactly one adapter per runtime, and nothing else may
build one. The runtime is fixed by the launcher you choose before any mutation, written into the
member record, and a runner whose adapter disagrees refuses to start. Each runtime's dangerous
flag — `--dangerously-skip-permissions`, `--dangerously-bypass-approvals-and-sandbox`, `--yolo` —
is disclosed and must be acknowledged before the first launch.

The lifecycle is `plan → execute → review → verify`, with at most **two** correction cycles. A
third rejection goes to a human; it never becomes an approval by attrition.

Status lives in the cmux sidebar rather than a pane you have to watch. The fleet never steals
focus, and it closes only workspaces whose identifier it recorded.

Requires cmux running. If the socket does not answer, the fleet says so and stops.

## The Kanban route

With Hermes present, `--via-kanban` turns approved phases into cards on the Hermes Kanban board
and lets its dispatcher run them, with board state mirrored into cmux. The bridge re-enforces the
approval gate itself, because the board has no opinion about approval. The idempotency key
carries the spec hash: relaunching returns the same card, an edited spec produces a new one.

What changes owner on that route is documented in `references/kanban.md`. Read it before using it.

## Known limits

- **Hermes has no post-compaction hook.** A long session that compacts over its first turn loses
  the bootstrap. If skills stop triggering, start a fresh session — this cannot be fixed from
  inside the plugin. Claude Code re-injects on `compact`; Codex discovers skills natively.
- **Per-dispatch model selection on Hermes is not established.** Until it is, route through the
  Kanban card's `--model`/`--provider`, or run inline. See `references/hermes-tools.md`.
- **The fleet needs cmux.** Everything else works without it.
- **Audit is opt-in and needs `sqlite3`.** Creating the database is what turns it on.

## Tests

```bash
python3 -m unittest tests.test_pwdev_power tests.test_power_hermes
```

`unittest discover` does not work in this tree: one form raises `ImportError`, the other runs zero
tests silently. Name the modules.

## License

Apache-2.0.
