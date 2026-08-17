# PWDEV Flow Marco 3 Design

## Objective

Complete the native Codex workflow of PWDEV Flow by adding discovery, design, planning, execution, product planning, curated memory, and simplification. The M1 quick, review, and verification skills remain compatible and consume the expanded runtime-neutral protocol.

## Scope

Marco 3 adds seven skills:

- `flow-discover` — frame a feature through a bounded interview and repository research;
- `flow-design` — turn approved requirements into the central eight-section specification;
- `flow-plan` — decompose a specification into dependency-aware waves and atomic tasks;
- `flow-execute` — implement approved tasks one at a time with fresh evidence;
- `flow-product` — create an approval-gated PRD and traceable roadmap;
- `flow-memory` — curate durable decisions, lessons, and conventions;
- `flow-simplify` — propose high-confidence behavior-preserving reductions and apply only approved proposals.

Audit, external CLI delegation, hooks, fleet orchestration, Docker isolation, and dashboards remain deferred.

## Architecture

Skills are thin runtime adapters. Detailed schemas and rules live in these neutral references:

- `discovery.md` — interview boundaries and discovery artifact schema;
- `specification.md` — the eight-section central contract and design gates;
- `planning.md` — wave and task contracts;
- `execution.md` — task lifecycle, advice, evidence, and correction rules;
- `product.md` — PRD and roadmap hierarchy;
- `memory.md` — memory lifecycle and relevance rules.

Existing `workflow.md`, `artifacts.md`, and `collaboration.md` are expanded rather than duplicated. All artifact paths remain under `.planning/flow/`.

## Full lifecycle

```text
DISCOVER → DESIGN → PLAN → EXECUTE → REVIEW → VERIFY
              ↑          │                    │
              │          └── advice/blocker   └── correction plan, max 2 cycles
              └──────────── human approval gates
```

Product planning precedes the feature lifecycle when a product-level contract is required. Memory is cross-cutting and read at phase boundaries. Simplification is optional between execution and review and has a mandatory proposal-approval gate.

## Human gates

- Discovery requirements require approval before design.
- Architecture decisions and the specification require approval before planning.
- The wave map and task plans require approval before execution.
- Simplification proposals require explicit ID-level approval before edits.
- Critical review findings block verification.
- Rejected verification may generate correction tasks; after two rejected correction cycles, stop for human direction.

## Execution policy

- Execute inline by default.
- Use collaborating workers only when the user explicitly requests subagents, delegation, or parallel agent work.
- Never run overlapping writers.
- Do not commit, push, create branches, or rewrite history without explicit user authorization.
- Preserve unrelated changes and stop on unsafe overlap.
- Every completion claim requires fresh commands run by the active runtime.

## Artifact model

```text
.planning/flow/
├── config.json
├── state.md
├── context/
│   ├── project.md
│   ├── requirements.md
│   ├── domain.md
│   ├── stack.md
│   └── pitfalls.md
├── product/
│   ├── prd.md
│   └── roadmap/<phase>/<epic>/<feature>/<task>.md
├── phases/<slug>/
│   ├── spec.md
│   ├── decisions.md
│   ├── plans/<id>-<slug>.md
│   ├── execution/<id>-summary.md
│   ├── review/
│   └── verify/
├── memory/
│   ├── MEMORY.md
│   └── <type>-<slug>.md
├── quick/
└── reports/
```

## Central specification

Every full feature uses one `spec.md` containing:

1. Persona and stack context;
2. Objective;
3. Inputs and business rules;
4. Output format and file boundaries;
5. Quality criteria;
6. Stop conditions;
7. Prohibitions;
8. Definition of done with executable evidence.

Downstream plans may clarify this contract but never silently weaken it.

## Memory model

Memories use Markdown frontmatter with `type`, `status`, `created`, `source`, `confidence`, and `related`. Valid types are `decision`, `lesson`, and `convention`; valid states are `active` and `superseded`. `MEMORY.md` indexes active entries without copying their full content. Skills select only relevant memories and must not treat memory as higher priority than current user instructions or repository governance.

## Failure handling

- Missing or conflicting requirements return to discovery.
- Architectural uncertainty returns to design.
- Unsafe task overlap returns to planning.
- An implementation blocker records a structured advice request and stops; it does not guess.
- Failed simplification verification leaves the proposal unapplied.
- Stale review evidence forces review to run again.

## Acceptance criteria

- All eleven Flow skills exist, have UI metadata, and pass the official skill validator.
- Six new neutral references exist and all local links resolve.
- The manifest version advances to `0.3.0` before the local cachebuster is applied.
- The plugin contains no Claude-specific runtime dependency or model routing.
- The official plugin validator and structural tests pass.
- Existing `pwdev-code`, `pwdev-feat`, `.claude/`, and `.planning/` changes remain untouched.
