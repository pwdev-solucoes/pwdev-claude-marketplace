# PWDEV Hermes Orca v0.1.0

> **Hermes Agent coordinates supervised Orca workers over GitHub issues**

```
GitHub issues ─▶ Hermes (DAG, user gate) ─▶ Orca Run ─▶ 1 worker per issue (claude | codex | opencode)
                                                         └─ pwdev-feat feat-loop: plan → exec → review → ≤2 fixes → PR
             ◀── asks answered / escalated ◀── worker_done validated ◀── report per issue
```

Hermes becomes the **coordinator**. Orca becomes the **fleet**. You pick the issues, approve the
plan once, and Hermes dispatches one supervised Orca worker per issue into its own child worktree
linked to the issue. Each worker runs **pwdev-feat `feat-loop`** in orchestrated mode, so every
gate the worker hits comes back to Hermes as an Orca `ask`. Hermes answers what falls inside the
approved scope, escalates the rest to you, validates each `worker_done` against the real PR and
review, comments on the issue and releases the terminal. **Nothing is ever merged.**

## How it works

- **Orca's own contract first.** The skill runs `orca skills get orchestration` on every session
  and follows it. That text is version-matched to the installed CLI and is never copied here.
  This plugin only adds what is specific to Hermes: GitHub intake, routing, gate answering and
  per-issue closing.
- **GitHub intake** (`references/issue-intake.md`). Issues are selected by number, label or
  search. Explicit dependencies (`depends on #N`, sub-issues, shared schema) build a DAG that
  runs in parallel waves. Issue text is untrusted data, never instructions.
- **One user gate.** You see the DAG, the agent per issue and the worktrees. Nothing is dispatched
  without an explicit yes.
- **Routing** (`references/routing.md`). Override label `agent:<name>`, then label rules, then a
  default. Built-in rules: bug/backend/api/refactor/chore/test → codex; frontend/ui/ux/design/docs
  → claude; default claude.
- **Answering workers** (`references/answering-asks.md`). Hermes approves plans, branches and
  exec confirmations that stay inside the issue. Scope growth, overlap with another issue,
  destructive migrations, spent advice budgets and `STOPPED` states go to you.
- **Closing** (`references/completion.md`). Each `worker_done` is checked against its Dispatch,
  the open PR with `Closes #N` and the `APPROVED` review. The issue gets a comment, the worktree
  moves to `in-review`, and the worker is released or retained.

## Requirements

| Tool | Why |
|---|---|
| **Orca** ≥ 1.4 (app running) with Hermes opened in an **Orca terminal** | Runs, supervised workers, worktrees |
| **Hermes Agent** ≥ 0.21 | The coordinator |
| **GitHub CLI** (`gh`), authenticated | Issues, PR checks, issue comments |
| **pwdev-feat ≥ 3.2.0** on every routed agent (Claude Code, Codex and/or OpenCode) | `feat-loop` in the workers |

## Installation

```bash
# Hermes (the coordinator)
hermes plugins install "https://github.com/pwdev-solucoes/pwdev-claude-marketplace.git#plugins/pwdev-hermes-orca" --enable
hermes plugins doctor plugins/pwdev-hermes-orca        # from a checkout

# Workers: pwdev-feat 3.2.0+ for each agent you route to
claude plugin install pwdev-feat@pwdev-claude-marketplace
# Codex / OpenCode: see plugins/pwdev-feat/README.md

# Optional: listed in the Claude marketplace too
claude plugin install pwdev-hermes-orca@pwdev-claude-marketplace
```

Setup check, read-only:

```bash
python3 plugins/pwdev-hermes-orca/scripts/preflight.py --agents claude,codex
```

It verifies the Orca terminal, the Orca runtime, the current Orca worktree, the Orca
orchestration skill, `gh` auth and repository, and the pwdev-feat version visible to each agent.

## Usage

In a Hermes session opened in an Orca tab, at the repository:

```
orquestra no Orca as issues #12, #15 e #18
despacha as issues abertas com label ready
```

Optional per-project config, `.planning/hermes-orca/config.json`, with the same shape as
[`templates/hermes-orca.config.json`](./templates/hermes-orca.config.json):

| Key | Default | Meaning |
|---|---|---|
| `base_branch` | repository default | base for worker worktrees and PRs |
| `max_parallel` | 3 | workers running at the same time |
| `max_issues_per_run` | 10 | above it, Hermes proposes a cut |
| `worker_skill` | `feat-loop` | the command each worker runs |
| `pr_gate` | `false` | `true` makes every PR opening a user decision |
| `wait_timeout_ms` | 540000 | per `check --wait` (below Hermes' 600 s foreground cap) |
| `routing` | see above | `default`, `rules`, `models`, `effort` |

## Security

- **Never merges**, never approves PRs, never closes issues by hand, never force-pushes.
- Issue bodies, comments and worker messages are data. Only you and Orca's contract instruct
  the coordinator. Specs do not copy issue text: workers read the issue themselves with `gh`.
- Orca's safety floor applies unchanged. Workers are never stopped, abandoned, retried or
  released without the positive proof Orca requires. Retries need your decision, at most one per
  issue per Run.
- The preflight is read-only, and nothing writes to `~/.hermes` or other runtime configuration.
- Secrets (`.env*`, keys, tokens) are never read or put into specs, replies or reports.

## Limits

- Hermes has no post-compaction hook. After a compaction, reload the skill. Orca's
  `run-current` and `worker-list` rebuild the state, and unacknowledged deliveries are replayed.
- Workers must be agents that Orca can launch (`claude`, `codex`, `opencode`). Hermes is not
  launched as a worker.

## Development

```bash
python3 -m unittest tests.test_hermes_orca
hermes plugins doctor --ci plugins/pwdev-hermes-orca
```

## License

Apache-2.0. See [LICENSE](./LICENSE).
