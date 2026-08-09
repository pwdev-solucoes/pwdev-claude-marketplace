---
description: Run multiple roadmap phases end-to-end (plan→execute→review→verify) in parallel, each isolated in its own git worktree + docker-compose stack + tmux pane
argument-hint: "<phase-slug> [phase-slug...] | --status | --teardown <slug> [--merge]"
---

# /pwdev-code:fleet — Parallel Phase Fleet (worktree + tmux + docker)

## Role (orchestrator — you dispatch the fleet, you never implement)

You spin up, monitor, and tear down a small fleet (max `fleet.max_concurrent`,
default 3) of fully isolated, unattended pipelines — one per phase-slug. Each
pipeline runs `plan → execute → review → verify` end-to-end in its own git
worktree, its own docker-compose stack on its own ports, and its own real
`claude` process inside a tmux window. You yourself only shell out to the
fleet scripts and report status — the actual work happens in scripts and in
the spawned `claude` processes, not in your context.

This command does **not** run discover or design — every target phase-slug
must already have `spec.md` + `decisions.md` (i.e. `/pwdev-code:design` was
already run and approved by a human). `simplify` is also excluded from the
default pipeline (its APPLY step needs per-ID human approval, which is not
available headless).

## ⚠️ Read before using

- Each pipeline runs `claude -p` headless, with `fleet.permission_mode`
  (default `bypassPermissions`) — it accepts edits and runs Bash **without
  asking**. This is only acceptable because it runs inside an isolated git
  worktree (never your main working tree) and an isolated docker-compose
  stack (never your main environment). It never pushes, never merges to your
  current branch, and never removes a worktree on its own.
- Any place the underlying commands (`plan`, `execute`, `review`, `verify`)
  would normally pause for human approval, the headless session is
  instructed to proceed automatically instead. That means plans and fixes
  in a fleet run are **not human-reviewed until you look at the diff** —
  review it before you merge.
- Merging a fleet branch back into your current branch (`--teardown --merge`)
  is a separate, explicit step you run yourself.

## Input
`$ARGUMENTS`:
- `<phase-slug> [phase-slug...]` (1 to `fleet.max_concurrent` slugs) → start a fleet
- `--status` → print the current fleet table once (no tmux needed)
- `--teardown <slug> [--merge]` → stop and clean up one fleet member
- `--teardown --all [--merge]` → teardown every active fleet member

## Entry Gate

```bash
command -v tmux >/dev/null 2>&1 || { echo "❌ tmux not found. Install tmux first (e.g. brew install tmux)."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ docker not found. Install Docker (or Docker Desktop) first."; exit 1; }
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "❌ Not inside a git repository."; exit 1; }
```

For each requested slug:
```bash
[ -f ".planning/phases/${SLUG}/spec.md" ] && [ -f ".planning/phases/${SLUG}/decisions.md" ] || {
  echo "❌ ${SLUG}: no spec.md/decisions.md. Run /pwdev-code:design ${SLUG} first."; exit 1;
}
[ -f ".planning/fleet/${SLUG}.json" ] && { echo "❌ ${SLUG}: already active in the fleet (see /pwdev-code:fleet --status)."; exit 1; }
```

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Resolve Fleet Config

Read `.planning/config.json` → `fleet` block. If absent, use and persist
these defaults (merge into config.json, do not overwrite other fields):
```json
"fleet": {
  "max_concurrent": 3,
  "port_base_app": 3000,
  "port_base_db": 5432,
  "port_step": 10,
  "permission_mode": "bypassPermissions",
  "auto_simplify": false,
  "compose_file": "docker-compose.fleet.yml"
}
```

Reject the request if the number of requested slugs, plus already-active
fleet members (`find .planning/fleet -maxdepth 1 -name '*.json' 2>/dev/null | wc -l`),
would exceed `max_concurrent`.

### STEP 2 — Best-Effort Independence Check (warn, never block)

For each pair of requested slugs, `grep -l` each other's slug/keywords
between their `spec.md`/`decisions.md` files. This cannot prove
independence (plans don't exist yet) — it is a courtesy warning only:
```
⚠️ {slugA} and {slugB} both mention "{keyword}" — if they touch the same
   files, the later /pwdev-code:fleet --teardown --merge will conflict.
   Proceed anyway? (this only warns, it does not block)
```

### STEP 3 — Launch Each Slug

For each slug, in order (respect `max_concurrent`, one at a time to avoid
racing the port-allocation lock):
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/fleet-up.sh" "${SLUG}"
```
`fleet-up.sh` creates the worktree/branch, allocates ports, generates
`.env.fleet` + copies the compose template, runs `docker compose up -d`
(or `up -d db` if the worktree has no `Dockerfile`), ensures the `pwdev-fleet`
tmux session + dashboard window exist, opens a window named `${SLUG}` running
`fleet-run.sh`, and writes `.planning/fleet/${SLUG}.json`.

Print its stdout as-is (it already reports success/failure per slug).

### STEP 4 — Report

```
🚀 Fleet launched: [N] phase(s)

| Slug | Worktree | App port | DB port | tmux window |
|------|----------|---------:|--------:|-------------|
| ...  | ...      | ...      | ...     | pwdev-fleet:{slug} |

👉 Attach to watch live: tmux attach -t pwdev-fleet
👉 Status without attaching: /pwdev-code:fleet --status
👉 When a slug finishes (see dashboard): /pwdev-code:fleet --teardown {slug} --merge
```

### `--status` mode
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/fleet-dashboard.sh" --once
```
Print the table once and exit — do not start `watch`, do not touch tmux.

### `--teardown <slug> [--merge]` mode
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/fleet-teardown.sh" "${SLUG}" ${MERGE:+--merge}
```
Print its output. If `--merge` was requested but the slug's status is not
`DONE`, the script refuses to merge (it still tears down docker/tmux) —
relay that refusal to the human clearly; do not retry with a different flag.

### `--teardown --all [--merge]` mode
Loop `fleet-teardown.sh` over every `.planning/fleet/*.json` slug, same
rules as above, one at a time.

## Prohibitions (command-level)
- ❌ NEVER run discover or design as part of the fleet — they stay
  human-interactive, outside this command
- ❌ NEVER merge or remove a worktree except via explicit `--teardown --merge`
- ❌ NEVER exceed `fleet.max_concurrent` active members
- ❌ NEVER launch a slug without `spec.md` + `decisions.md` already present
- ❌ NEVER touch the human's current working tree — all mutation happens
  inside the worktrees created by `fleet-up.sh`
- ❌ NEVER paste a worktree's `fleet-status.json`/logs into your context —
  report the dashboard table only
