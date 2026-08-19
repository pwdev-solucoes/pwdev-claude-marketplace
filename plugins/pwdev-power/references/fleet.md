# Fleet

A fleet runs approved phases in parallel, each in its own Git worktree and its own Docker stack.
It is the only part of this plugin that constructs a privileged provider command, so it is also
the part with the most rules.

Two modes, and the difference is who drives:

- **Visual (default)** — 1 to 4 members share **one** cmux workspace, one pane each, every pane an
  interactive provider session seeded with that phase's brief. A human watches all of them and
  steers any of them. No structured results, no correction cap: the human is the loop.
- **Autonomous (`--auto`)** — one workspace per member running the stage machine below,
  unattended, with structured results and up to two correction cycles.

Read [safety](safety.md) and [cmux](cmux.md) before operating one.

## The panel

**One panel at a time, 1 to 4 members.** Four panes is where a grid stops being readable, and an
unreadable panel defeats the point. A second panel is refused rather than merged into the first:
growing a live panel would mean splitting into its workspace and typing a privileged command into a
running shell, and every packaged script exists to avoid exactly that.

The whole grid is created in **one** `new-workspace --layout` call. Each layout surface carries its
own `command`, so a member's session starts from a shell-quoted file — the same guarantee the
autonomous runner has, for the same reason.

**Members bind themselves to their panes.** Each pane writes its own `CMUX_SURFACE_ID` to
`fleet/<slug>.surface` before exec-ing the provider. Pairing panes to slugs by index would be a
guess, and it goes wrong the moment layout order and pane order disagree; the pane's own report
cannot. A member whose pane never reported is usable but not tearable-down in isolation, and the
launcher says so.

## Entry gate

A slug may launch only when all of these hold:

1. The repository has a named current branch and a clean enough tree to reason about.
2. `.planning/power/features/<slug>/spec.md` exists and contains **exactly one**
   `Status: APPROVED` field. "Exactly one" is deliberate: a document with a second one inside
   an example block is ambiguous, and ambiguity here means launching unapproved work.
3. `.planning/power/features/<slug>/plan.md` exists.
4. The human has acknowledged the privileged vector of the runtime you are.
5. cmux answers `ping`.

Hash the **exact approved working-tree bytes** of `spec.md` and `plan.md`, not stale `HEAD`
bytes — approved contracts are frequently not committed yet. Those hashes bind the member.

`spec.md` stays frozen for the whole run. `plan.md` does not, and cannot: the `plan` stage writes
`features/<slug>/plan.md`, so holding it to the launch hash would stop every member on its own
first stage — on the artifact it was told to produce, not on a tampered contract. The plan stage is
therefore guarded by `spec.md` alone, and `plan.md` is re-bound from the bytes that stage
committed. From `execute` onwards both contracts are strict again.

## Configuration defaults

Merged defaults-first into `config.json` so every existing known or unknown field wins:

```json
{
  "fleet": {
    "port_base_app": 3000,
    "port_base_db": 5432,
    "port_step": 10,
    "compose_file": "docker-compose.power-fleet.yml",
    "permission_mode": "danger-full-access",
    "auto_simplify": false
  }
}
```

Reject any `permission_mode` other than `danger-full-access`, and require `auto_simplify` to
be the exact JSON boolean `false`. Never overwrite an existing permission mode to a dangerous
value on the human's behalf.

## Provisioning, under the allocation lock

- **Worktree**: `<repo-parent>/<repo-name>-fleet-<slug>` on branch `power-fleet/<slug>`. A
  sibling of the repository, not a child, so it never shows up as untracked inside it.
- **Ports**: first free slot, not an incrementing counter, so teardown releases a slot for reuse.
  A slot is free only when all four hold: its index is unclaimed, its ports are in range, they
  collide with no member's, and neither answers a live probe of `127.0.0.1`. All four are checked
  **inside** the search, so a port the host already uses advances to the next slot instead of
  refusing the launch — somebody's own Postgres on 5432 is not a reason to reject a fleet on a
  machine with sixty-three free slots. The probe is racy by nature; a port free at probe time can
  be taken before Docker binds it, and Docker is the right place for that failure to surface.
- **Compose**: copy the packaged template, publish atomically with check-copy-recheck through
  a same-directory `mktemp` plus rename. Bind published ports to `127.0.0.1` only.
- **`.env.fleet`**: write under `umask 077` **before** the content lands, not `chmod` after.
  The throwaway password must never exist world-readable, not even for an instant.
- **`.gitignore`**: generate one inside the worktree covering `.env.fleet`, the compose file,
  `fleet-status.json`, `fleet-logs/` and `fleet-results/`. The runner stages with `git add -A`
  and teardown `--merge` lands that history on the human's base branch — this file is what
  stops a password and raw provider stdout from riding along.
- **cmux**: one workspace per slug, created with `--focus false`, its UUID recorded.

## Member record — `.planning/power/fleet/<slug>.json`

Written with `jq -n` to a temporary file and published by atomic rename. Carries at minimum:
`slug`, `runtime`, `mode`, `branch`, `worktree_path`, `cmux_workspace_id`, `cmux_surface_id`,
`app_port`, `db_port`, `port_index`, `spec_sha256`, `plan_sha256`, `status`, `created_at`,
`updated_at`, and `kanban_task_id` when the Kanban route is used. `schema_version` is 2.

`mode` is `visual` or `auto`. It is recorded rather than inferred: a visual member has no runner
status file, and so does a member whose runner crashed before writing one. Guessing from the
absence would report a crash as a design.

`status` is one of `ACTIVE`, `RUNNING`, `DONE`, `NEEDS_HUMAN`.

## Runner status — `<worktree>/.planning/power/fleet-status.json`

`{ slug, stage, status, message, verdict, correction_cycles, updated_at }` where `stage` is one
of `plan`, `execute`, `review`, `verify`, `execute-fix`, `review-fix`; `status` is `OK`,
`DONE`, `FAILED` or `NEEDS_HUMAN`; `verdict` is `NONE`, `APPROVED`, `CAVEATS` or `REJECTED`;
and `correction_cycles` is an integer 0–2.

`DONE` appears only on the terminal `verify`, and only for `APPROVED` or `CAVEATS`. A
`REJECTED` that exhausts the cap becomes `NEEDS_HUMAN` — it never becomes an approval by
attrition. The provider's own result vocabulary is narrower (`OK`, `FAILED`, `NEEDS_HUMAN`):
`DONE` is the runner's word, not the provider's.

## Ownership

The provider leads its own process group. Prove the **whole group** absent before validating a
result, committing, publishing status, or advancing a stage — reaping a successful leader does
not release ownership, because it may have left dev servers, watchers or child containers
alive. When ownership cannot be proven, retain the runner lock: an orphaned lock is a
deliberate signal that a human must look, not a bug.

## Correction cap — autonomous mode only

`plan → execute → review → verify`. On `REJECTED`, up to **two** cycles of
`execute-fix → review-fix → verify`. A third rejection is `NEEDS_HUMAN`, never `DONE`. Worst
case is ten provider invocations.

Each accepted stage requires a **fresh artifact** — compare a snapshot of the stage's artifact
directory before and after. Well-formed JSON that describes work nobody did is the failure
mode this catches.

## Reporting

Report per slug: stage, status, branch, ports, and a message truncated to 60 characters. Never
print absolute worktree paths, full logs, prompts, or result payloads. The dashboard is a
status line, not a transcript.

The runner repairs the two result deviations that carry no information rather than failing a stage
over them: a `message` past the schema's cap is trimmed, and a `verdict` missing outside `verify`
is set to `NONE`, the only value allowed there. On `verify` the verdict stays required — there it
*is* the result. Everything else stays strict: wrong stage, unknown key, unknown status, or
anything that is not one JSON object is still a failed stage.

Only Codex is held to the schema natively; Claude and Hermes read it as prose, and prose is not
reliably honoured. What protects the work is the contract hashes and the fresh-artifact check, not
the shape of its summary.

## Teardown

Without `--merge`: stop the stack, close the member's cmux surface (visual) or workspace (auto),
remove the member record, and **preserve the branch and the worktree**. A panel member closes its
own pane; the shared workspace goes only with the last member out. With `--merge`: refuse anything that is not `DONE`,
verify the terminal status schema again, then merge.

`docker compose down` never gets `--volumes`. The named volume outlives the member; report it
with the command to remove it and let the human decide.
