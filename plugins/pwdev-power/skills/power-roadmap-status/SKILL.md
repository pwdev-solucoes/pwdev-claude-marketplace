---
name: power-roadmap-status
description: Use when the status, progress, completeness, traceability, or next valid action of a PWDEV Power product roadmap is requested
---

# Roadmap Status

Report the roadmap's health from its durable artifacts. This workflow is **read-only**: never
create, repair, approve, reject, or otherwise edit an artifact while reporting status.

Read [artifacts](../../references/artifacts.md) and
[collaboration](../../references/collaboration.md) before acting.

## Sources of truth

Inspect these paths when they exist:

1. `.planning/power/config.json` for the configured response language.
2. `.planning/power/state.md` for the recorded status, last gate, active artifact, and next action.
3. `.planning/power/product/prd.md` for requirement approval and scope.
4. `.planning/power/product/roadmap/ROADMAP.md` for the roadmap index.
5. `.planning/power/product/roadmap/TRACEABILITY.md` for requirement-to-roadmap coverage in
   both directions.
6. `.planning/power/product/roadmap/RISKS.md`, `METRICS.md`, `ROLLOUT.md`, and the phase, epic,
   and feature files beneath the roadmap root for completeness and counts.

Missing files are findings, not reasons to invent state. Do not treat the existence of a PRD or
roadmap as approval. Human gate results recorded in `state.md`, plus the PRD's explicit approval
field where applicable, are authoritative.

## Assessment

Determine the lifecycle state without changing it:

- `NOT_INITIALIZED`: `.planning/power/state.md` is absent.
- `NO_REQUIREMENT`: state exists but `prd.md` does not.
- `REQUIREMENT_DRAFT`: the PRD exists without exactly one `Status: APPROVED` field.
- `READY_FOR_ROADMAP`: the requirement is approved but `ROADMAP.md` is absent.
- `ROADMAP_INCOMPLETE`: the roadmap exists but a mandatory artifact, hierarchy link, source
  reference, acceptance criterion, or bidirectional traceability entry is missing or malformed.
- `AWAITING_ACCEPTANCE`: the roadmap is structurally complete but `state.md` does not record the
  human roadmap gate as approved.
- `ACCEPTED`: `state.md` records the roadmap gate as approved and the files remain structurally
  complete.
- `BLOCKED`: `state.md` records a blocked gate; report its recorded reason when present.

Count unique roadmap IDs using the hierarchy defined by `power-product`: phase, epic, feature,
and task. Detect duplicate IDs, broken parent relationships, index links whose targets do not
exist, features without acceptance criteria, and requirement references absent from either side
of `TRACEABILITY.md`. Do not estimate percentage progress from file counts: the artifacts do not
define task completion as roadmap progress.

## Response contract

Reply in the configured language with a compact status report containing:

```text
ROADMAP: <lifecycle state>
GATE: <last recorded roadmap gate or none>
COUNTS: <phases> phases | <epics> epics | <features> features | <tasks> tasks
TRACEABILITY: PASS | FAIL | UNAVAILABLE — <one-line reason>
HEALTH: PASS | WARN | FAIL — <one-line reason>
NEXT ACTION: <the exact next valid action>
FINDINGS: <none, or concise actionable items>
```

Use `UNAVAILABLE` counts when no roadmap exists. Prefer the `Next:` value in `state.md` when it is
consistent with the artifacts; otherwise explain the mismatch and give the next safe action.
Keep findings tied to paths or IDs. Never paste whole artifacts.

This is product-roadmap status, not execution status. If the user asks about isolated feature
runs, stages, worktrees, ports, or runners, use `power-fleet --status` instead.
