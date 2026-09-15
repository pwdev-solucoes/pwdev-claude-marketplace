# SDD Composy — Portable Spec-Driven Development

> [Versão em português](./README.pt-BR.md)

## Origin and adaptation

This plugin is a fork of the Spec-Driven Development methodology implemented by
[Rodrigo Branas](https://github.com/rodrigobranas) and
[Pedro Nauck](https://github.com/pedronauck). It is adapted to the PWDEV workflow
and intended for use with [Compozy](https://github.com/compozy/compozy).

SDD Composy is an approval-gated workflow packaged for Claude Code, Codex, Hermes Agent, and
OpenCode. All four runtimes use the same lifecycle, schemas, skills, references, scripts, and
templates; a workflow can move between hosts without changing its meaning. Packaged support and
offline adapter tests do not constitute real-provider acceptance: unavailable, unauthorized, or
unaffordable runs must be reported as `BLOCKED` or `NOT_RUN`, never as `PASS`.

Human-readable contracts live under `tasks/prd-<slug>/`. Operational state lives under
`.planning/sdd-composy/`. Generated project Markdown targets OKF v0.2, requires a non-empty
`type`, and permits unknown extension fields. Supported JSON and Markdown updates preserve
unknown fields.

## Setup and artifact language

Run `/sdd-composy:init` (or its equivalent below) before generating any artifact, passing `pt-BR`
or `en-US` to select the language of human-facing artifacts. If the language is omitted, init
asks you to choose and writes no artifacts until a choice is made. The selection is persisted in
`.planning/sdd-composy/config.json`; every downstream skill consumes it without asking again, and
before initialization returns `{"status":"not_initialized","next_action":"run_init"}`.

PRDs, stories, TechSpecs, task descriptions, QA/evidence reports, and status prose follow the
selected language. Machine keys, IDs, schemas, filenames, lifecycle values, command names, and
user evidence remain unchanged. Invalid language values fail without changing the existing
configuration. See the [language contract](./references/language.md).

## Runtime entry points

| Runtime | Discovery | Invocation |
| --- | --- | --- |
| Claude Code | `.claude-plugin/plugin.json` | `/sdd-composy:<name>` thin commands |
| Codex | `.codex-plugin/plugin.json` (`skills` root) | `$sdd-<name>` — the skill's `name` |
| Hermes Agent | `.hermes-plugin/plugin.yaml`; the bootstrap registers the 17 skills | `skill_view("sdd-composy:sdd-<name>")` |
| OpenCode | linked skill folders (see below) | `/sdd-<name>` commands or the native `skill` tool |

**OpenCode** has no plugin mechanism for skills: it discovers `SKILL.md` folders
([opencode.ai/docs/skills](https://opencode.ai/docs/skills)) and custom commands next to them. The
bundled installer links the 17 skills and generates the 17 `/sdd-<name>` commands, globally
(`~/.config/opencode/{skills,command}`) or in one project:

```bash
python3 plugins/sdd-composy/.opencode-plugin/install.py              # global
python3 plugins/sdd-composy/.opencode-plugin/install.py --project .  # this project only
python3 plugins/sdd-composy/.opencode-plugin/install.py --uninstall  # remove what it installed
```

It links, never copies: `scripts/`, `references/`, and `templates/` are reached through the
link. A Claude Code *plugin* install lives in Claude's plugin cache and does not make the skills
visible to OpenCode; the installer does. `LOOP` and headless `FLEET` members run on OpenCode through
`scripts/loop-engine-opencode.py` with the vector `opencode run --dir <worktree> --format json
[--auto]`; an interactive fleet member opens `opencode <worktree> --prompt`. See
[opencode-tools.md](./references/opencode-tools.md).
Offline adapter tests establish support, not real-provider acceptance.

Automated Hermes LOOP/fleet execution uses `hermes -z <prompt> --in <worktree>` only after
independent isolation is established or the user gives specific consent. No adapter falls back
to another provider, and Hermes Kanban integration is not implemented. The shared core remains
authoritative for lifecycle gates, artifacts, state transitions, safety, and orchestration. See
the exact [runtime contract](./references/runtime.md).

## Commands

| Claude Code | Codex / OpenCode | Serves |
| --- | --- | --- |
| `/sdd-composy:init` | `$sdd-init` / `/sdd-init` | INIT — workspace, governance, language |
| `/sdd-composy:map` | `$sdd-map` / `/sdd-map` | MAP — read-only codebase evidence |
| `/sdd-composy:prd` | `$sdd-prd` / `/sdd-prd` | PRD — human product contract |
| `/sdd-composy:stories` | `$sdd-stories` / `/sdd-stories` | STORIES — from an approved PRD |
| `/sdd-composy:techspec` | `$sdd-techspec` / `/sdd-techspec` | TECHSPEC — from approved contracts |
| `/sdd-composy:tasks` | `$sdd-tasks` / `/sdd-tasks` | TASKS — import, inspect, advance |
| `/sdd-composy:execute` | `$sdd-execute` / `/sdd-execute` | EXECUTE — one task in `ready` |
| `/sdd-composy:qa` | `$sdd-qa` / `/sdd-qa` | QA — task in `qa_required` |
| `/sdd-composy:evidence` | `$sdd-evidence` / `/sdd-evidence` | EVIDENCE — task in `evidence_required` |
| `/sdd-composy:review` | `$sdd-review` / `/sdd-review` | REVIEW — task in `review_required` |
| `/sdd-composy:verify` | `$sdd-verify` / `/sdd-verify` | VERIFY — task in `verify_required` |
| `/sdd-composy:quick` | `$sdd-quick` / `/sdd-quick` | QUICK — bounded change, at most five files |
| `/sdd-composy:loop` | `$sdd-loop` / `/sdd-loop` | LOOP — bounded correction of one task |
| `/sdd-composy:fleet` | `$sdd-fleet` / `/sdd-fleet` | FLEET — isolated worktrees for ready tasks |
| `/sdd-composy:sync` | `$sdd-sync` / `/sdd-sync` | Markdown/JSON task synchronization |
| `/sdd-composy:status` | `$sdd-status` / `/sdd-status` | Read-only consolidated status |
| `/sdd-composy:trace` | `$sdd-trace` / `/sdd-trace` | Append-only semantic trace |

## Workflow

```text
INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS
                                            |
                              EXECUTE -> QA -> EVIDENCE -> REVIEW -> VERIFY -> COMPLETE
```

Product and execution gates require explicit human approval; editing operational JSON is not a
way to simulate approval. Verification reproduces fresh evidence. The reduced `QUICK`, bounded
`LOOP`, and isolated `FLEET` paths keep the same durable contracts and safety rules. A fleet
runs only ready tasks from the task projection of a human-approved TechSpec, each in its own
branch and Git worktree; a headless fleet also needs the recorded approval of the run
(`--human-approved --approved-by`), and nothing is merged automatically. The launch gate, the
headless result, Compose, and teardown rules are in the [fleet contract](./references/fleet.md).

## State, compatibility, and recovery

Human intent and approval records live in Markdown under `tasks/prd-<slug>/`; validated JSON
under `.planning/sdd-composy/` is authoritative for current operational state, and
synchronization requires an explicit authority choice when they diverge. Status inspection is
read-only, and init never replaces an existing `.claude`. See [status](./references/status.md)
and the [runtime contract](./references/runtime.md).

## Independence and security

SDD Composy has no runtime dependency on `pwdev-flow` or `pwdev-feat`. It never infers
approval, reads secrets or fleet environment files, or merges fleet branches automatically. Do
not skip approval, QA, evidence, or verification gates. Full contracts are in
[`references/`](./references/).

## License

Apache-2.0. See [LICENSE](../../LICENSE).
