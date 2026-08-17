# Curated memory contract

Memory stores durable project knowledge, not conversation transcripts. Current user instructions and repository governance always outrank memory.

## Types

- `decision` — an approved architectural or product choice and its rationale;
- `lesson` — evidence-backed knowledge from a failure, rejection, or incident;
- `convention` — a stable repository pattern confirmed by code or governance.

## Entry schema

Store `.planning/flow/memory/<type>-<slug>.md` with frontmatter:

```yaml
---
type: decision
status: active
created: 2026-08-16
source: .planning/flow/phases/example/decisions.md
confidence: high
related: []
---
```

The body contains statement, evidence, scope, consequences, and invalidation condition. Valid statuses are `active` and `superseded`. Never delete historical entries as the default forget operation; mark them superseded with reason and replacement.

## Index

`.planning/flow/memory/MEMORY.md` lists active entries in one line each: type, link, scope, confidence, and related names. Keep the index concise and do not duplicate full bodies.

## Operations

- `capture` — validate durability, evidence, type, and duplicate risk before writing;
- `list` — show active entries, optionally filtered by type or scope;
- `show` — read one entry and its direct relations;
- `link` — add a symmetric relation between two existing entries;
- `supersede` — retain history and record reason or replacement;
- `select` — choose memories relevant to a phase or task.

## Relevance

Select direct matches first, then at most one relation hop. Prefer decisions for design, conventions for planning and execution, and lessons for review and verification. Keep the selection small enough to explain why each entry matters. Flag contradictions instead of choosing silently.
