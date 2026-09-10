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

With `--compose`, the launcher owns the Compose project and records its exact project, file,
port, branch, and worktree in `resources`. Teardown trusts the validated nested ownership
record, not legacy top-level mirrors; it runs `docker compose down` only for those recorded
resources. A missing or mismatched resource, failed Compose shutdown, dirty merge target,
invalid result, or failing post-merge verification stops cleanup and preserves branch,
worktree, and metadata for recovery. Without `--merge --confirm CONFIRM-SDD-MERGE`, teardown
preserves the branch and worktree.

The adapters and lifecycle have offline regression coverage. That is installed support, not a
claim that real Hermes, Codex, or Claude Code acceptance has passed; real-provider acceptance
is deferred to the acceptance harness.
