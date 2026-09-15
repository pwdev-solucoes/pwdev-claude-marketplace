# Fleet core

The fleet runs several ready tasks in parallel, one isolated Git worktree per member, each
driven by exactly one bound LOOP. It never infers approval and never merges automatically.

## Launch gate

`launch.sh --runtime claude|codex|hermes|opencode --root ROOT --fleet-id ID --base-branch BRANCH
--task .planning/sdd-composy/tasks/<prd-slug>.json [--ui auto|cmux|tmux|headless] [--compose]
[--human-approved --approved-by <kind:actor>] [--prepare-only]`

- The task contract is the canonical task projection under `.planning/sdd-composy/tasks/`, whose
  file name matches its `prd_slug`, and `tasks/prd-<slug>/techspec.md` must carry
  `lifecycle.status: APPROVED`, `human_approval: APPROVED`, and a `verified` event. Anything else
  stops the launch before any branch, worktree, or record exists. `--prepare-only` skips this
  gate and the runner, and only prepares worktrees and records.
- From a projection the fleet takes only its `ready` tasks; dependency completion is read from
  that same projection. A single task object with dependencies is refused, because its
  dependencies cannot be proven.
- Tasks need stable `TASK-NNN` IDs, acceptance criteria, verification commands, and safe,
  non-symlink, non-overlapping `allowed_paths`.
- The fleet ID must start with a letter or digit; it is validated before it names a directory.
- A headless fleet runs the LOOP unattended, so it requires `--human-approved --approved-by
  <kind:actor>` given only after the human approved this run. The approval is recorded as
  `approval: {by, at}` in every member; the runner refuses a member without it.

`launch.sh` creates a plugin-owned `sdd-fleet/<fleet-id>/<TASK>` branch and a sibling worktree,
binds the contract SHA-256, allocates a port under a lock that times out, creates one LOOP per
member, and then starts the selected `cmux`, `tmux`, or `headless` adapter. Failures before a UI
resource exists roll back everything that invocation created; later failures preserve recovery
state. UI handles are presentation only and never own lifecycle truth. `.env.fleet` is never read.

## Interactive boundary and status

Interactivity belongs only to fleet. There is exactly one task and one isolated worktree per
member, and exactly one existing bound LOOP per interactive member. An isolated LOOP remains
non-interactive outside fleet; neither a cmux/tmux pane nor a headless process creates another
LOOP or changes its identity. An interactive member (cmux or tmux) opens the runtime session for
a human through `interactive-run.sh`; native LOOP approval is asked inside that session.

`dashboard.sh` is read-only. For an interactive member it projects runtime, UI, member ID,
task ID, bound LOOP ID, the complete recorded handle including unknown fields, interaction state,
timestamps, and `next_action` directly from authoritative member JSON. Missing optional fields
remain absent and displayed values are sanitized recursively. Status does not call UI status,
flash, or other presentation mutations, even with `--handle`. Terminal capture is diagnostic only
and never satisfies a witness, evidence, review, verification, or approval gate.

## Headless run and result

`run.sh` (started by the headless adapter) holds the member runner lock, runs the bound LOOP
through `scripts/loop-engine-<runtime>.py` in the worktree with the LOOP record in the main
repository, and stops the whole provider process group on termination. Authorization comes from
`SDD_<RUNTIME>_ISOLATED=1` or `SDD_<RUNTIME>_AUTOMATION_CONSENT=1` and
`SDD_FLEET_PERMISSION_MODE`; each stage contract also carries `loop_id` and `loop_root`, so the
VERIFY command record is written below the main repository.

When the LOOP stops, the runner publishes the member result:

- LOOP `completed` and every change inside `allowed_paths`: the changes are committed on the
  member branch, and the member becomes `completed` with that `commit`.
- A change outside `allowed_paths`, or a LOOP stop that needs a human: `blocked`, no commit.
- Any other stop (iteration cap, environment failure): `failed`.

The result is written to `.planning/sdd-composy/fleet/<fleet-id>/results/<member>.json`
([fleet-result.schema.json](../schemas/fleet-result.schema.json)), the member records
`result_path`, `finished_at`, `message`, and `commit`, and `state.json` gets the member summary.
A pane, terminal capture, or UI state is never completion evidence; merge and completion require
human approval.

## Record authority

Fleet metadata lives under `.planning/sdd-composy/fleet/<fleet-id>/`. Schema v2 member records
require an explicit `runtime` (`claude-code`, `codex`, `hermes`, or `opencode`), canonical
absolute `repository_root` and `worktree_path`, an `owner` identity, and nested `resources`. A
member without a bound LOOP cannot run: relaunch it. Do not hand-edit a member or global state to
manufacture readiness, completion, or approval.

## Provider and resource ownership

Runtime vectors and engine adapters are listed in [runtime.md](runtime.md); there is no
cross-provider fallback.

With `--compose`, the launcher copies the template to the single central path
`.planning/sdd-composy/fleet/<fleet-id>/docker-compose.yml`, hashes that exact file, and starts
it once with project name `sdd_fleet_<fleet-id>` and the fleet-owned `runtime.env`. Every
member's nested `resources` records the repository-relative `compose_file`,
`compose_project`, `compose_sha256`, and `compose_allocated: true`, alongside its port, branch,
and worktree. Without `--compose`, the record explicitly contains `compose_allocated: false`.

## Teardown

`teardown.sh --root ROOT --fleet-id ID --member-id TASK [--merge --confirm CONFIRM-SDD-MERGE]`

1. Validates the member identity, resources, and (for a merge) the result, the contract hash, a
   clean repository on the fleet's recorded base branch, and a result commit equal to the member
   branch tip.
2. Stops the member's UI resource and runner through its adapter (`fleet_ui_teardown`); a runner
   that cannot be stopped preserves every record.
3. Runs `docker compose down --env-file runtime.env` only when this is the last member of the
   fleet; the shared project stays up for the others. The central file, project name, and
   `compose_sha256` are validated first.
4. Without `--merge`: releases the member port and record, keeping branch and worktree.
   With `--merge`: `git merge --no-ff`, the bound verification commands, worktree removal, and
   deletion of the merged branch.

A missing flag, file, digest, or mismatched resource; failed shutdown; dirty or wrong merge
target; invalid result; or failing post-merge verification stops cleanup and preserves branch,
worktree, and metadata for recovery.

The adapters and lifecycle have offline regression coverage, including a full headless run with a
provider double. That is installed support, not a claim that real Hermes, Codex, OpenCode, or
Claude Code acceptance has passed.
