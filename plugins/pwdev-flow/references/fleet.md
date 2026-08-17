# Autonomous fleet contract

Use this contract for `flow-fleet`. Fleet lifecycle mutations belong to the packaged scripts; the skill owns intent, dangerous-mode acknowledgement, configuration merging, advisory overlap review, and concise reporting.

## Configuration

Merge this default `fleet` block into `.planning/flow/config.json` only after the dangerous-mode acknowledgement:

```json
{
  "fleet": {
    "max_concurrent": 3,
    "port_base_app": 3000,
    "port_base_db": 5432,
    "port_step": 10,
    "permission_mode": "danger-full-access",
    "auto_simplify": false,
    "compose_file": "docker-compose.flow-fleet.yml"
  }
}
```

Require the configuration root and any present `.fleet` block to be JSON objects. Before merging, reject every explicitly present `permission_mode` other than `"danger-full-access"`, including null or a non-string value; never silently upgrade it.

Use a defaults-first recursive object merge so existing known and unknown fields win while missing known fields are filled. The executable operation shape is:

```text
fleet_defaults='{"max_concurrent":3,"port_base_app":3000,"port_base_db":5432,"port_step":10,"permission_mode":"danger-full-access","auto_simplify":false,"compose_file":"docker-compose.flow-fleet.yml"}'
temporary=$(mktemp .planning/flow/.config.json.XXXXXX)
jq --argjson fleet_defaults "$fleet_defaults" '
  if type != "object" then error("Flow config must be an object")
  elif has("fleet") and (.fleet | type) != "object" then error("fleet must be an object")
  elif ((.fleet // {}) | has("permission_mode")) and .fleet.permission_mode != "danger-full-access"
    then error("fleet permission_mode must be danger-full-access")
  else .fleet = ($fleet_defaults * (.fleet // {}))
  end
' .planning/flow/config.json >"$temporary" && mv "$temporary" .planning/flow/config.json
```

Remove the owned temporary file after any failure. Do not alter the source file unless validation and merge both succeed. Require positive integer capacity and ports, deterministic `port_step`, the exact JSON boolean `auto_simplify: false`, and the exact packaged Compose filename `docker-compose.flow-fleet.yml` before launch; reject string lookalikes and alternate paths. Represent any supported extra arguments as JSON string-array elements and never evaluate configuration as shell code.

## Entry gate and authorization

Before launch, require:

- a Git repository on a named current branch;
- local `git`, `jq`, `docker`, `tmux`, `python3`, `shasum` and the binary of the selected runtime (`codex` or `claude`), plus Docker Compose v2;
- one to `fleet.max_concurrent` valid lowercase slugs;
- exactly one `Status: APPROVED` field in both `.planning/flow/phases/<slug>/spec.md` and `decisions.md`;
- no central member, `flow-fleet/<slug>` branch, sibling worktree, allocation-lock, or port collision;
- free deterministic application and database ports;
- explicit acknowledgement of the dangerous flag of the selected runtime.

Show the exact command shape of that runtime before acknowledgement, and never the other one:

```text
codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral --cd <worktree> --output-schema <fleet-result-schema> --output-last-message <result-file> <autonomous-prompt>
claude -p --dangerously-skip-permissions --no-session-persistence --output-format json <autonomous-prompt>
```

Each vector is built in exactly one place, `fleet-engine-<runtime>.sh`, and nothing else may construct a provider command or add a permission flag. No configuration value, environment variable, argument, or portable state field may turn one vector into the other: the runtime is fixed by the launcher chosen before any mutation, is bound into the central member, and a runner whose adapter disagrees with that member refuses to start.

Codex enforces the result shape natively through `--output-schema`. Claude Code has no equivalent, so its adapter carries the same contract inside the prompt and converts the `--output-format json` envelope into the structured result, failing closed when the final message is not exactly one matching JSON object.

This acknowledgement authorizes only the requested fleet launch and its isolated stage commands. It does not authorize unrelated subagents, standalone delegation, merges, or other dangerous commands.

For multiple slugs, compare `spec.md` and `decisions.md` text for repeated repository paths. Warn about matches as advisory overlap; never reject independent work automatically.

## Packaged interfaces

Resolve these files relative to the installed skill and invoke them without copying or reimplementing their lifecycle commands:

```text
fleet-up.sh <lowercase-slug>                                        # Codex launcher
claude-fleet-up.sh <lowercase-slug>                                 # Claude launcher
fleet-dashboard.sh [--once]
fleet-teardown.sh <lowercase-slug> [--merge]
fleet-run.sh <lowercase-slug> <worktree-path> [danger-full-access]  # shared runner
claude-fleet-run.sh <lowercase-slug> <worktree-path> [danger-full-access]
```

Both launchers reach the same `fleet-up.sh` provisioning and both panes reach the same `fleet-run.sh` lifecycle; the `claude-*` entry points only pin the runtime identity. `fleet-run.sh` is started by the launcher inside tmux. Do not invoke either runner as a substitute for launch preflight.

## Worktree, ports, Docker, and tmux

Under the central `.planning/flow/fleet/.lock`, allocate the first unused zero-based port index. Derive `app_port = port_base_app + port_step * index` and `db_port = port_base_db + port_step * index`.

Create `flow-fleet/<slug>` and sibling `<repository>-fleet-<slug>`. Hash the exact approved working-tree bytes of that slug's `spec.md` and `decisions.md`, not stale `HEAD` bytes. In the isolated worktree, atomically replace each absent or byte-different contract and commit only the isolated contract changes. Bind both hashes, the canonical initiating root, the initiating named branch, and the base commit into central state. Never stage or commit the initiating working tree.

Publish `.gitignore`, the packaged `docker-compose.flow-fleet.yml`, and a newly generated mode-0600 `.env.fleet` through same-directory temporary files and atomic renames. Refuse pre-existing Compose or environment destinations and reject symlinks or non-regular destination chains. Never read, display, audit, reuse, or adopt a project `.env.fleet`. Start the full Compose project when a Dockerfile exists; otherwise start only `db`. Use project `flow-fleet-<slug>`.

Use shared tmux session `pwdev-flow-fleet`, window `dashboard`, and one `<slug>` window. Atomically write mode-0700 `.planning/flow/fleet/<slug>.pane.sh` with a shell-quoted `exec <runtime-runner> <slug> <worktree> danger-full-access` vector, where the runner is `fleet-run.sh` for Codex and `claude-fleet-run.sh` for Claude. Persist the bound central member with `ACTIVE` status before asking tmux to consume that central pane wrapper. Never create or execute a worktree-local pane wrapper.

## State schemas

Store central bookkeeping at `.planning/flow/fleet/<slug>.json` and the bound pane command at `.planning/flow/fleet/<slug>.pane.sh`; never execute a pane file before the member is `ACTIVE`:

```json
{
  "slug": "example",
  "runtime": "codex",
  "branch": "flow-fleet/example",
  "worktree_path": "/absolute/sibling/example",
  "app_port": 3000,
  "db_port": 5432,
  "port_index": 0,
  "project_name": "flow-fleet-example",
  "tmux_window": "pwdev-flow-fleet:example",
  "compose_file": "docker-compose.flow-fleet.yml",
  "spec_sha256": "<64 lowercase hexadecimal characters>",
  "decisions_sha256": "<64 lowercase hexadecimal characters>",
  "initiating_root": "/absolute/canonical/repository",
  "base_branch": "main",
  "base_commit": "<40 to 64 lowercase hexadecimal characters>",
  "status": "ACTIVE",
  "created_at": "2026-08-16T12:00:00Z",
  "updated_at": "2026-08-16T12:00:00Z",
  "worktree_created": true,
  "docker_attempted": true,
  "tmux_attempted": true
}
```

Store per-worktree status at `.planning/flow/fleet-status.json`:

```json
{
  "slug": "example",
  "stage": "verify",
  "status": "DONE",
  "message": "verification approved",
  "verdict": "APPROVED",
  "updated_at": "2026-08-16T12:30:00Z",
  "correction_cycles": 0
}
```

Allow stages `plan`, `execute`, `review`, `verify`, `execute-fix`, and `review-fix`; statuses `RUNNING`, `ACTIVE`, `DONE`, and `NEEDS_HUMAN`; verdicts `NONE`, `APPROVED`, `CAVEATS`, and `REJECTED`. Before merge side effects, require the exact terminal status schema: matching slug, `stage: verify`, `status: DONE`, verdict `APPROVED` or `CAVEATS`, non-empty message and timestamp, and integer `correction_cycles` from 0 through 2. Treat malformed or identity-mismatched state as requiring explicit recovery.

Keep stage logs under `.planning/flow/fleet-logs/` and structured results under `.planning/flow/fleet-results/`. Never copy full logs, prompts, result content, or absolute worktree paths into dashboard or audit output.

## Autonomous stages

Run `PLAN → EXECUTE → REVIEW → VERIFY` sequentially by invoking the canonical Flow skills. Before and after every dangerous provider call, revalidate the registered worktree, central member, exact contract identities, and bound SHA-256 values. Require structured `stage`, `status`, `message`, and `verdict` results and a fresh stage artifact. Invalid output, non-zero provider exit, missing artifact, changed contracts or worktree identity, or explicit stop becomes `NEEDS_HUMAN`.

Run each provider stage in its own process group. Reaping a successful provider leader does not release ownership: prove the complete group absent before result validation, commit, status publication, audit, or the next stage. On `HUP`, `INT`, or `TERM`, stop the complete descendant group with a bounded `TERM` grace period followed by `KILL` if necessary; only after group absence may the runner remove owned temporaries, publish `NEEDS_HUMAN`, emit its audit event, and release the runner lock. If absence cannot be proven, fail closed without terminal publication and retain the runner lock as an explicit recovery marker.

Commit scoped changes only inside the fleet branch after each successful stage. If verification is `REJECTED`, run `execute-fix → review-fix → verify`. Stop after at most two rejected correction cycles. Mark `DONE` only for final `APPROVED` or `CAVEATS`.

## Dashboard and reporting

Use `fleet-dashboard.sh --once` for status reports. Report slug, app/database ports, stage, status, branch, updated timestamp, truncated message, and the validated central worktree path. Live mode refreshes every five seconds inside tmux. Do not open full logs for routine status.

## Teardown, merge, and recovery

Teardown validates the exact derived central pane as a regular, non-symlinked executable before side effects. Permit an absent pane only for a bound `NEEDS_HUMAN` partial launch whose bookkeeping proves `tmux_attempted: false`. Then attempt the member's Docker Compose shutdown and tmux window termination. Without `--merge`, remove the pane if present and the central member only after resource shutdown is verified; preserve branch and worktree. For `--teardown --all`, validate central member filenames and invoke teardown separately for each slug.

Pass `--merge` only after explicit user authorization. Require the strict terminal status above, a clean tracked worktree, no non-fleet untracked files, and the initiating repository still on the member's bound base branch. Merge with `--no-ff`; on conflict, abort and preserve branch, worktree, central pane, and recoverable state. Remove the worktree, central pane, and member bookkeeping only after a successful merge. Use `DRY_RUN=1` only to preview exact commands; its rendered state, contract binding, guards, and atomic publications must match live behavior.

Teardown stops the Compose project without `--volumes`: it never destroys data on its own. The member's named database volume therefore survives, and teardown reports its exact name so it can be reclaimed deliberately.

On partial launch, persist `NEEDS_HUMAN` with known resources and report the exact teardown route. Preserve bookkeeping after any cleanup verification failure. Never delete unknown files, recursively clean unresolved paths, or repair malformed state automatically.

## Audit and prohibitions

When audit is enabled, record `fleet_launched` only after `ACTIVE` is durably published and the tmux launch succeeds, `fleet_stage` only after each sanitized status transition is atomically published, and `fleet_teardown` only after the requested stop or merge is verified. Audit is best-effort: warn without reporting early success or replacing the lifecycle result. Limit detail to slug, stage, status, exit code, timeout, and safe relative targets. Never record the autonomous prompt, stdout, environment, model, credentials, `.env.fleet`, or an absolute worktree path.

Never launch without dangerous-mode acknowledgement, run outside the registered worktree, mutate the initiating working tree, auto-merge, reuse legacy `.planning/fleet`, bypass correction limits, or convert an advisory overlap warning into an automatic block.
