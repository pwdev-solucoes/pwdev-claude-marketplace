---
name: flow-fleet
description: Launch, inspect, and tear down autonomous Codex phase fleets in isolated Git worktrees. Use when approved Flow phase slugs should run in parallel, when fleet status is requested, or when a fleet member must be stopped or explicitly merged.
---

# Operate a Flow Fleet

Read [fleet](../../references/fleet.md), [safety](../../references/safety.md), [artifacts](../../references/artifacts.md), and [collaboration](../../references/collaboration.md) before acting.

## Route

Interpret only these routes:

- `<slugs>`: launch one or more approved lowercase phase slugs.
- `--status`: invoke packaged `fleet-dashboard.sh --once`.
- `--teardown <slug>`: invoke packaged `fleet-teardown.sh <slug>` and preserve its branch and worktree.
- `--teardown --all`: enumerate validated `.planning/flow/fleet/<slug>.json` entries and invoke packaged teardown once per slug.

Pass `--merge` to teardown only when the user explicitly requests it. Never merge a non-`DONE` member or translate state into legacy paths.

## Launch

1. Inspect repository status, confirm a named current branch, inspect `.planning/flow/config.json`, and inspect the requested approved `spec.md` and `decisions.md` contracts. Never read `.env.fleet`.
2. Resolve scripts from this installed skill at `../../scripts/`; call only packaged fleet and audit scripts for lifecycle operations.
3. Before the first launch, display this exact autonomous command shape:

   ```text
   codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral --cd <worktree> --output-schema <fleet-result-schema> --output-last-message <result-file> <autonomous-prompt>
   ```

4. Require explicit acknowledgement of `--dangerously-bypass-approvals-and-sandbox`. Do not persist a missing fleet block or launch a member before acknowledgement. Reject a configured `permission_mode` other than `danger-full-access`.
5. After acknowledgement, require the configuration root and any existing `.fleet` value to be objects. Reject an existing `permission_mode` unless it is exactly `danger-full-access`; require the exact JSON boolean `auto_simplify: false` and exact packaged Compose filename before launch.
6. Merge the exact defaults from [fleet](../../references/fleet.md) into both absent and partial fleet blocks with `jq`: set `.fleet = ($fleet_defaults * (.fleet // {}))`. Write through a same-directory temporary file and atomically rename it only after validation. This defaults-first recursive merge fills missing known fields while every existing known or unknown field wins; never overwrite permission mode to dangerous.
7. For multiple slugs, compare their specification and decision text for repeated repository paths. Emit an advisory overlap warning with the matching paths; let the human decide and never block automatically.
8. Invoke packaged `fleet-up.sh <slug>` once per acknowledged slug. The script binds exact contract hashes and initiating branch/base identity, and rejects unsafe symlinked state paths. Stop launching further members after any failure and report the recovery state.

## Report

Invoke the one-shot dashboard and report each slug, worktree, app/database ports, stage, status, branch, and concise message. Do not load or reproduce full fleet logs, prompts, or result payloads. When audit is enabled, record only the allowed semantic metadata described in [audit](../../references/audit.md).
