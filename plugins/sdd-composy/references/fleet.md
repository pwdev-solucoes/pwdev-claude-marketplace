# Fleet core

The fleet core accepts only ready task contracts with explicit acceptance criteria,
verification commands, complete dependencies, safe non-symlink paths, and no path overlap.
`launch.sh` creates a plugin-owned `sdd-fleet/<id>` branch and a sibling worktree while leaving
the central worktree untouched. Every member record binds the task contract SHA-256, branch,
and worktree. A lock serializes launch state; failures before provider dispatch remove only
resources created by that invocation, while later failures preserve recovery state.

Unless `--prepare-only` is selected, the launcher validates every member and its approved phase
contracts, then starts the requested provider through the selected `cmux`, `tmux`, or
`headless` adapter. UI handles are presentation only and never own lifecycle truth. The fleet
never merges automatically. `.env.fleet` is never read.

## Record authority and migration

Fleet metadata lives under `.planning/sdd-composy/fleet/<fleet-id>/`. Schema v2 member records
require an explicit `runtime` (`claude-code`, `codex`, or `hermes`), canonical absolute
`repository_root` and `worktree_path`, an `owner` identity, and nested `resources`. Normal
execution diagnoses any non-v2 member as `legacy fleet member requires explicit migration`.
It never silently upgrades or discards one.

An eligible, complete schema v1 record for Claude Code or Codex can be migrated with:

```sh
scripts/fleet/run.sh --migrate-member MEMBER.json --root ROOT
```

Migration validates the exact Git root, independent registered worktree/branch, terminal
evidence when applicable, confined paths, identities, and enums; it preserves unknown fields
and publishes the v2 record atomically. Legacy Hermes records are not supported because v1 did
not define Hermes. Do not hand-edit a member or global state to manufacture readiness or
approval.

## Provider and resource ownership

The runtime vectors are `claude -p`, `codex exec`, and
`hermes -z <prompt> --in <worktree>`. There is no cross-provider fallback. Hermes automation
also requires proven isolation or specific user consent. Hermes Kanban is not implemented and
is unavailable.

With `--compose`, the launcher copies the template to the single central path
`.planning/sdd-composy/fleet/<fleet-id>/docker-compose.yml`, hashes that exact file, and starts
it once with project name `sdd_fleet_<fleet-id>` and the fleet-owned `runtime.env`. Every
member's nested `resources` records the repository-relative `compose_file`,
`compose_project`, `compose_sha256`, and `compose_allocated: true`, alongside its port, branch,
and worktree. Without `--compose`, the record explicitly contains `compose_allocated: false`;
teardown then skips Compose and does not require a file or digest.

For an allocated Compose resource, teardown requires the boolean flag, validates repository,
fleet/member owner, branch/worktree, exact central path and project name, rejects symlinks, and
compares the current central file with `compose_sha256`. Only then does it run
`docker compose --project-name <project> -f <central-file> down`. It does not resolve the file
inside a member worktree or trust legacy top-level mirrors. A missing flag, file, digest, or
mismatched resource; failed Compose shutdown; dirty merge target; invalid result; or failing
post-merge verification stops cleanup and preserves branch, worktree, and metadata for
recovery. Without `--merge --confirm CONFIRM-SDD-MERGE`, teardown removes the member record
after successful resource shutdown while preserving the branch and worktree.

The adapters and lifecycle have offline regression coverage. That is installed support, not a
claim that real Hermes, Codex, or Claude Code acceptance has passed; real-provider acceptance
is deferred to the acceptance harness.
