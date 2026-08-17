# PWDEV Flow workflow

PWDEV Flow separates portable development contracts from runtime-specific orchestration. Project artifacts define what must happen; the active coding agent decides how to use its available planning, filesystem, terminal, and collaboration capabilities.

## Core phases

`DISCOVER → DESIGN → PLAN → EXECUTE → REVIEW → VERIFY`

Each phase has an explicit input, durable output, and human-visible gate. The full lifecycle uses [discovery](discovery.md), [specification](specification.md), [planning](planning.md), and [execution](execution.md) contracts. Review and verification consume the same artifacts without trusting prior summaries.

Product work may start with [product planning](product.md). [Memory](memory.md) is cross-cutting and selected at phase boundaries. Simplification is optional between `EXECUTE` and `REVIEW`.

## Gate rules

- Never execute an unapproved architectural plan.
- Never mark execution complete from an implementation summary alone.
- Critical or major review findings block approval.
- Verification uses fresh evidence and may reject prior claims.
- A rejected verification may produce bounded correction tasks.
- Stop after two failed correction cycles and request human direction.

## Phase outputs

| Phase | Required output | Approval gate |
|---|---|---|
| DISCOVER | context and approved requirements | requirements approved |
| DESIGN | central specification and decisions | specification approved |
| PLAN | wave map and atomic plans | execution scope approved |
| EXECUTE | code changes and evidence summaries | all planned tasks resolved |
| REVIEW | correctness findings and QA evidence | no blocking finding |
| VERIFY | adversarial truth table and verdict | completion proved |

Do not skip a gate because the next phase appears straightforward. When a gate is rejected, update the producing artifact rather than patching downstream assumptions.

## Quick path

`SCOPE → MINI_PLAN → IMPLEMENT → TEST → REVIEW → VERIFY`

Quick mode is limited to five implementation files and excludes migrations, destructive operations, and unresolved architectural decisions. Crossing a boundary changes the required workflow; stop and recommend the full phase sequence before editing further.

## State transitions

Valid states are `INITIALIZED`, `PLANNED`, `EXECUTING`, `REVIEW_REQUIRED`, `VERIFY_REQUIRED`, `COMPLETE`, `REJECTED`, and `BLOCKED`. Update state only after the corresponding evidence exists. Preserve the previous state and explain the blocker when a transition cannot be completed.

For full features, also use `DISCOVERING`, `DESIGNING`, and `PLANNING` while their artifacts are incomplete. `COMPLETE` is terminal for the active phase but does not prevent a new feature from starting.

## Semantic audit at gates

When configuration has `"audit": true`, record the semantic outcome after it succeeds: phase start/completion, artifact write, decision, gate approval/rejection, memory change, simplification, archive, or migration. Use the packaged helper and the vocabulary in [audit](audit.md). A disabled audit is a successful no-op; an audit write failure is reported but does not rewrite the already-known gate result.
