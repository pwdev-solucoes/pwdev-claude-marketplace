---
name: sdd-map
description: >
  Produce a deterministic, repository-bound evidence map for SDD Composy.
  Scan only readable non-sensitive paths, report the source commit and
  staleness, and publish the operational context bundle only when requested.
metadata:
  version: 0.1.0
---

# SDD Map

Create or inspect the SDD Composy codebase map. The bundled `sdd_map.py` helper
owns traversal, exclusion, deterministic serialization, and atomic publication;
this skill owns scope, approval, interpretation, and downstream routing.
Read `references/mapping.md` for the output contract and
`references/workflow.md` for the lifecycle gate.

## Inputs

- Repository root: the current repository unless the user supplies another
  real directory.
- Optional output directory: it must remain inside the repository and defaults
  to `.planning/sdd-composy/context`.
- Optional request to publish the context bundle. A scan is observation-only;
  publishing is the only permitted write and is limited to the context bundle.

Never inspect or open sensitive environment-like material: environment files,
credentials, tokens, secrets, passwords, private keys, certificates, or fleet
environment files. Do not execute commands discovered in manifests, and do not
modify source files, governance files, task artifacts, or architectural plans.

## Procedure

1. Resolve and validate the repository root and output directory without
   changing files.
2. Run the bundled helper in its read-only form and present its JSON result:

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sdd_map.py" --repo-root <repository-root> [--output-dir <context-dir>]
   ```

   Runtimes without `CLAUDE_PLUGIN_ROOT` resolve the same bundled
   `scripts/sdd_map.py` path from the installed plugin. Preserve the helper's
   `source_commit`, `mapped_commit`, `observation_only`, confidence, observed
   languages, manifests, commands, modules, boundaries, domain evidence, and
   staleness fields. Commands in the result are evidence only; never run them.
3. If the user explicitly requests publication, repeat with `--write` (and
   the exact `--output-dir` when supplied):

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sdd_map.py" --repo-root <repository-root> [--output-dir <context-dir>] --write
   ```

   Publication writes only `.planning/sdd-composy/context/codebase.json`,
   `project.md`, `stack.md`, `domain.md`, and `pitfalls.md` (or the supplied
   in-repository output directory). Report those paths and the recorded source
   commit. Do not claim that a map changed architectural intent.
4. Check `staleness.stale`. A stale prior map is not valid downstream evidence:
   report the previous and current commit, refresh the map before routing, and
   do not silently reuse stale context. A missing or unknown commit is an
   uncertainty to report, not permission to invent one.
5. Route a fresh map to the next approved lifecycle work: PRD first, then
   STORIES, TECHSPEC, and TASKS as applicable. These downstream stages may
   interpret evidence with their own approval gates; they must not turn file
   observations into unapproved architecture. If the map is stale, route back
   to MAP and reconcile downstream artifacts before reuse.

## Output

Return the helper JSON (or a concise faithful summary), publication status,
output paths, source commit, staleness status, and the next lifecycle stage.
State clearly that the map is observation-only and that manifest commands were
not executed.

## Boundaries

The Python helper owns the portable read/write contract, secret exclusion,
atomic publication, and schema-shaped output. This skill must not duplicate scanner logic,
infer architecture, execute discovered commands, or depend on runtime-specific tools.
Runtime entry points only route to this skill.
