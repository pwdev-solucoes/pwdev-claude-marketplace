---
name: sdd-fleet
description: Coordinate ready SDD tasks in isolated worktrees with explicit runtime and cmux adapters.
---

# `$sdd-fleet`

## Workspace language

Before generating artifacts, run the bundled `scripts/sdd_language.py <repo-root>`.
Consume only the persisted `.planning/sdd-composy/config.json` language. If the
result is `not_initialized`, return it with `next_action: run_init`; do not ask
for a language here. For `pt-BR`, write human narrative, summaries, descriptions,
and labels in Brazilian Portuguese; for `en-US`, use English. Translate template
placeholder prose when rendering, preserving IDs, schema keys, enum values,
filenames, commands, and parser-required headings. Do not translate user evidence.

Use this portable skill to launch, inspect, and tear down an isolated fleet of
approved SDD task contracts. Fleet accepts only `ready` tasks with complete
dependencies, explicit acceptance criteria, known verification commands, and no
confirmed path overlap. It never infers approval and never merges fleet
branches automatically.

Interactivity belongs only to fleet. Each member owns one task, one isolated
worktree, and exactly one existing bound LOOP. An isolated LOOP remains
non-interactive when it is not launched as a fleet member. UI presentation never
changes that binding or grants lifecycle authority.

## Operations

- `launch`: validate contracts and create recoverable branches/worktrees.
- `status`: inspect fleet/member records without changing state.
- `teardown`: stop or explicitly confirm a merge for a terminal member.

Use `scripts/fleet/launch.sh`, `run.sh`, `dashboard.sh`, and `teardown.sh` for
the shared lifecycle. Runtime command vectors belong only to
`engine-claude.sh` and `engine-codex.sh`. The cmux adapter is presentation-only:
it must not own process lifecycle truth, and cmux operations stay inside the
workspace created by this fleet. Prefer cmux when available, with tmux or
headless as explicit fallbacks.

`status` is read-only. Project runtime, UI, member, task, bound LOOP ID, the
complete recorded handle (including unknown fields), interaction state, timestamps,
and `next_action` from authoritative member JSON without filling in missing optional
fields. Sanitize every displayed value recursively. Even with `--handle`, status
does not call UI status, flash, or other presentation mutations. Terminal capture
is diagnostic only: it never satisfies witness,
evidence, review, verification, or an approval gate.

Before launch, report the selected tasks, runtime, UI adapter, branch/worktree
paths, verification commands, and safety checks. Never read or adopt an
existing `.env.fleet`; preserve recoverable branches and worktrees after any
failure. A merge requires an explicit confirmation token and successful
identity/result verification. Human approval remains required; the fleet never
merges a branch or treats a pane, terminal capture, or UI state as completion.
