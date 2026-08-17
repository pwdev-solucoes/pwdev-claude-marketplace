# Maintenance contract

Maintenance preserves project history. It may inventory, archive, or generate changelog content; it never deletes artifacts or rewrites Git history.

## Inventory

Classify Flow artifacts as:

- active — referenced by current state or an unapproved gate;
- complete — verification verdict is `APPROVED` and state no longer depends on it;
- stale — references missing files, conflicts with state, or has superseded evidence;
- archivable — complete and not required by active product, memory, migration, or audit state.

Always keep config, state, context, product contracts, memory, audit data, migration records, and the active phase.

## Archive

1. Run inventory read-only and list exact source paths, evidence of completion, size, and proposed destination.
2. Require explicit approval of the exact targets.
3. Resolve `.planning/flow/archive/<date>/` and reject collisions rather than overwriting.
4. Move only approved complete phase or quick-task directories.
5. Update state references when needed and record an `archived` audit event when audit is enabled.
6. Verify every source is absent, every destination exists, and no unapproved path changed.

Never archive a phase without an approved verification artifact. Never use recursive deletion or cleanup of unknown files.

## Changelog

Generate entries from real Git commits and verified Flow summaries. Detect an explicit version or use `Unreleased`. Classify Conventional Commit prefixes into Added, Fixed, Changed, Performance, Tests, Documentation, and Maintenance.

If `CHANGELOG.md` exists, preserve all content and insert the new section in the correct position. Do not duplicate commit hashes, fabricate descriptions, or include reverted work without a note. Present a preview before writing unless the user already asked to generate the file.
