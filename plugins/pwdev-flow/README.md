# PWDEV Flow — Portable Spec-Driven Development

> [Versão em português](./README.pt-BR.md)

Approval-gated software development that runs natively in **both Claude Code and
Codex** from one source package. The workflow lives in runtime-neutral skills and
references; each host gets a thin adapter over the same contracts.

```
DISCOVER ─▶ DESIGN ─▶ PLAN ─▶ EXECUTE ─▶ [SIMPLIFY] ─▶ REVIEW ─▶ VERIFY
```

Every phase has an explicit input, a durable artifact, and a human-visible gate.
A workflow started in one runtime can be continued in the other: both read and
write the same `.planning/flow` artifacts.

## Install

Claude Code:

```bash
claude plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
claude plugin install pwdev-flow@pwdev-claude-marketplace
```

Codex reads the same package through `.codex-plugin/plugin.json` and invokes the
skills as `$flow-<name>` instead of slash commands.

## Commands

| Command | Purpose |
|---|---|
| `/pwdev-flow:init` | Initialize, inspect, resume, or migrate the portable `.planning/flow` workspace |
| `/pwdev-flow:discover` | Gather and get approval for bounded requirements |
| `/pwdev-flow:design` | Produce the central specification and its decisions |
| `/pwdev-flow:plan` | Decompose an approved specification into atomic tasks |
| `/pwdev-flow:execute` | Execute an approved plan with bounded corrections |
| `/pwdev-flow:review` | Review an implementation or an explicit file set |
| `/pwdev-flow:verify` | Adversarially verify, with fresh evidence, that the phase is done |
| `/pwdev-flow:simplify` | Analyze a completed phase and apply approved simplifications |
| `/pwdev-flow:quick` | Deliver a small bounded change (up to five implementation files) |
| `/pwdev-flow:product` | Create an approval-gated product requirement |
| `/pwdev-flow:memory` | Curate or query durable project memory |
| `/pwdev-flow:health` | Diagnose repository and workspace health without changing anything |
| `/pwdev-flow:audit` | Record, inspect, summarize, or verify semantic audit events |
| `/pwdev-flow:maintenance` | Inventory, archive, or summarize artifacts safely |
| `/pwdev-flow:compat` | Inspect or plan migration from legacy PWDEV Code artifacts |
| `/pwdev-flow:delegate` | Delegate a bounded task to a guarded external coding CLI |
| `/pwdev-flow:fleet` | Launch, inspect, or tear down isolated autonomous phase fleets |

## The shared artifact protocol

Everything lives under `.planning/flow/`: `config.json`, `state.md`, phase
contracts under `phases/<slug>/`, memory, reports, and fleet bookkeeping. The
`runtime` field in `config.json` records which adapter last initialized the
workspace; it is metadata and never makes artifacts unreadable from the other
host.

## Autonomous fleets

`/pwdev-flow:fleet` runs approved phases in parallel, each in its own Git
worktree with its own Docker Compose stack and tmux pane. Each member runs
`PLAN → EXECUTE → REVIEW → VERIFY` unattended, commits per stage inside its own
branch, and stops after at most two rejected correction cycles.

The two runtimes drive their own headless CLI:

```text
codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral --cd <worktree> --output-schema <schema> --output-last-message <result> <prompt>
claude -p --dangerously-skip-permissions --no-session-persistence --output-format json <prompt>
```

Each vector is built in exactly one adapter, `scripts/fleet-engine-<runtime>.sh`,
and nothing else may construct a provider command or add a permission flag. The
runtime is fixed by the launcher you choose, before any mutation, and is bound
into the central member — a runner whose adapter disagrees with that member
refuses to start. Everything else — locks, contract hashes, process-group
ownership, result validation, commits, the correction cap — is shared.

**A fleet launch requires explicit acknowledgement of the dangerous flag of its
runtime.** That acknowledgement authorizes only the requested launch.

## Delegation

`/pwdev-flow:delegate` hands a bounded task to an allowlisted external CLI
(Codex, OpenCode, Kimi, Gemini, Kiro). The packaged runner builds argument
arrays, never shell strings; previews the exact expanded vector with a SHA-256
confirmation token; enforces a write lock and a read-only mutation check; and
never inherits fleet authorization. The primary agent must review the resulting
diff independently — a delegated summary is never proof.

## Audit

Opt-in through `"audit": true`. Events are appended to
`.planning/flow/audit/events.jsonl` **only after** the described action actually
happened, and carry semantic metadata only — never prompts, provider output,
environment, or absolute paths.

Claude hooks are deliberately absent: hook telemetry would be host-specific and
could be mistaken for a portable workflow trail.

## Safety posture

- Read and write only inside the repository and explicitly authorized locations.
- Never read or expose `.env` files, credentials, tokens, keys, or `.env.fleet`.
- Never commit, push, branch, or mutate external services without authorization.
- Run the command that proves each completion claim; never trust a summary.
- Stop after two failed correction cycles and ask for human direction.

## Layout

```text
plugins/pwdev-flow/
├── .claude-plugin/plugin.json   # Claude manifest
├── .codex-plugin/plugin.json    # Codex manifest
├── commands/                    # 17 Claude command adapters
├── skills/                      # 17 portable skills
├── references/                  # shared workflow and safety contracts
├── scripts/                     # lifecycle plus one adapter per runtime
└── templates/                   # result schema and fleet Compose stack
```

## License

Apache-2.0. See [LICENSE](../../LICENSE).
