---
name: sdd-sync
description: Reconcile SDD Composy task Markdown and JSON safely through an explicit inspect, plan, and approved apply workflow.
metadata:
  version: 0.1.0
---

# SDD Sync

Synchronize the human task contracts and operational JSON projection without
silently selecting an authority. Read `references/synchronization.md`,
`references/tasks.md`, and `references/safety.md` before operating. This skill
is portable and runtime-neutral.

## Operations

Use the bundled `${CLAUDE_PLUGIN_ROOT}/scripts/sdd_sync.py` helper (or the
same bundled path resolved by another runtime) for every operation:

- `inspect <markdown-root> <state> [--root]` is read-only and reports stable,
  deterministic classifications, including conflicts and malformed inputs.
- `plan <markdown-root> <state> [--root]` is read-only and produces the exact
  plan and input fingerprints that an apply must consume.
- `apply <markdown-root> <state> <plan-json-path> --authority markdown|json
  --confirmation-token CONFIRM-SDD-SYNC [--root]` is the only mutating
  operation. It requires explicit human approval for the selected authority;
  never infer approval from a plan, a clean inspection, or model confidence.

The CLI loads the JSON emitted by `plan` from `plan-json-path` and forwards it
to the guarded apply API; it does not implement a second synchronization
algorithm.

Present inspect and plan results before asking for approval. A stale plan,
changed input, invalid authority, missing exact `CONFIRM-SDD-SYNC` token,
symlink, malformed artifact, or unresolved conflict must stop the operation.
Markdown/JSON conflicts are never overwritten silently. After apply, report
the helper's post-apply verification and the exact paths changed. The helper
owns repository confinement, same-directory temporary files, atomic
replacement, unknown-field preservation, and deterministic output; do not
duplicate those policies in this skill.

## Output and boundaries

Return the operation, repository-bound paths, classifications, selected
authority (if any), approval status, plan/token status, verification result,
and next permitted action. Inspection and planning must not write files.
Do not read or expose `.env`, credentials, tokens, private keys, certificates,
or fleet environment files. Do not mutate external services or commit.
