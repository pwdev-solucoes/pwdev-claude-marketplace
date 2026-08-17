---
name: flow-maintenance
description: Inventory, archive, and summarize PWDEV Flow project history safely. Use when the user asks to find stale artifacts, archive completed work, clean the Flow workspace without deletion, or generate a changelog from verified history.
---

# Maintain PWDEV Flow History

Read [maintenance](../../references/maintenance.md), [artifacts](../../references/artifacts.md), [audit](../../references/audit.md), and [safety](../../references/safety.md) before proposing changes.

## Route

- `inventory` is read-only and classifies each candidate as active, complete, stale, or archivable.
- `archive` moves only explicitly approved, verified-complete phase or quick-task directories.
- `changelog` derives a preview from real Git commits and verified Flow execution summaries.

If the request is ambiguous, begin with `inventory`; it does not authorize archiving.

## Inventory

1. Read state, active product and phase contracts, verification verdicts, memory links, migration records, and audit references.
2. List exact candidate paths, classification evidence, size, dependencies, and proposed archive destination.
3. Preserve config, state, context, product contracts, memory, audit data, migration records, and the active phase.

## Archive

1. Produce the inventory and require explicit approval for the exact source paths and destinations.
2. Resolve destinations below `.planning/flow/archive/<date>/`; refuse every collision instead of overwriting.
3. Move only approved directories whose verification verdict is `APPROVED` and which are no longer active.
4. Update authorized state references, then record `archived` through [flow_audit.py](../../scripts/flow_audit.py) when audit is enabled.
5. Verify that every approved source moved, every destination exists, and no unapproved path changed.

## Changelog

Read actual Git history and verified Flow summaries. Use an explicit version or `Unreleased`, preserve existing `CHANGELOG.md` content, exclude fabricated or reverted work, and present a preview before writing unless the user already authorized file generation.

## Constraints

- Never delete artifacts, use recursive cleanup, rewrite Git history, or archive incomplete work.
- A stale artifact is a finding, not automatically an archive candidate.
- Do not infer approval for archive targets from a general cleanup request.

## Output

Return `MODE`, inventory or changelog preview, exact changes made if any, verification evidence, `STATUS`, and `NEXT`.
