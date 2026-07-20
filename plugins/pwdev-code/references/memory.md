# Project Memory Protocol

Curated, durable project knowledge that survives phases and sessions.
Managed by `/pwdev-code:memory`; consumed by orchestrator commands when
building subagent spawn prompts; fed automatically by the verify/review loops.

## Layout

`.planning/memory/` — **versioned in git** (curated knowledge belongs to the
repo; do NOT gitignore it). One file per memory + a cheap index:

```
.planning/memory/
├── MEMORY.md                          # index — 1 line per ACTIVE memory
├── decision-prefer-postgres-jsonb.md
├── lesson-migrations-need-rollback.md
└── convention-service-suffix.md
```

## Memory file format — `{type}-{name}.md`

```markdown
---
name: prefer-postgres-jsonb
description: Use Postgres JSONB for flexible fields — MongoDB rejected (existing infra)
type: decision            # decision | lesson | convention
created: 2026-07-18
source: design:user-auth  # {command}:{phase-slug} that captured it, or "manual"
status: active            # active | forgotten
related: [service-suffix] # optional — names (not filenames) of related memories
---

## Context
{2-6 lines: what happened / why it matters}

## Rule
{the actionable instruction an agent must follow — 1-3 lines}

## Evidence
{optional: paths, report excerpt, commit hash}
```

Types:
- **decision** — durable technical/product decision (and its "why not").
- **lesson** — something that went wrong and must not repeat (fed by verify/review).
- **convention** — a project pattern agents must follow (naming, layering, style).

## Memory graph (relations)

Memories form a lightweight graph: `related:` in the frontmatter is the
canonical edge list (directed, source → target, by `name`). `[[name]]` links
in the body are accepted as input — `/pwdev-code:memory` consolidates them
into `related:` on capture. Edges are mirrored into the index as a `[rel:]`
suffix so selection can traverse WITHOUT opening any memory file.

## Index format — `MEMORY.md`

One line per ACTIVE memory, fixed grammar (nothing else in the file body):

```markdown
# Project Memory Index
<!-- managed by /pwdev-code:memory — one line per ACTIVE memory; edit via the command -->

- `decision` prefer-postgres-jsonb — Use Postgres JSONB for flexible fields (memory/decision-prefer-postgres-jsonb.md) [rel: service-suffix]
- `lesson` migrations-need-rollback — Verify rejected user-auth: always test down() migrations (memory/lesson-migrations-need-rollback.md)
- `convention` service-suffix — Services end in *Service under app/Services (memory/convention-service-suffix.md)
```

The `[rel: name1, name2]` suffix is OPTIONAL and always comes last, after the
`(path)`. Lines without it are valid — older indexes keep working. Only
`/pwdev-code:memory` writes the index; it keeps `related:` and `[rel:]` in
sync (capture, link, forget).

## Curation rules

- `description` ≤ 120 chars — it is what selection reads; make it searchable.
- A memory is **durable**: it matters beyond the current phase. Phase trivia
  stays in decisions.md / verify.md, never here.
- Max ~30 active memories — beyond that, `/pwdev-code:memory` suggests consolidating.
- Dedupe by `name` before writing (update the existing file instead).
- `forget` never deletes the file: set `status: forgotten` and drop the index
  line (the file remains as an audit trail).

## Selection algorithm (for spawn prompts)

Orchestrators load memory cheaply and precisely:

1. Read ONLY `MEMORY.md` (never scan the directory).
2. Select **≤5** seed entries by keyword overlap between each line's
   name/description and the task scope (file paths, domain terms, phase slug).
3. Priority by consumer:
   - executor / code-reviewer / simplifier → `convention` first
   - verifier → `lesson` first
   - design (main context) → `decision` + `convention`
   - advisor → `decision` first
4. **Graph expansion (1 hop):** collect the names in the seeds' `[rel: ...]`
   suffixes, in seed order. Add each one that has an ACTIVE index line and is
   not already selected, up to a TOTAL cap of **7** entries. Names without an
   active line (forgotten/nonexistent) are silently ignored. Expansion never
   reads memory files and never runs without seeds.
5. No seed match → **omit the block entirely** (never inject an empty section).

## RELEVANT MEMORY block (canonical template)

Inject paths, not pasted content — the subagent reads only what it needs:

```
RELEVANT MEMORY — curated project knowledge; treat as binding constraints:
- [convention] service-suffix — Services end in *Service under app/Services
  → read .planning/memory/convention-service-suffix.md
- [lesson] migrations-need-rollback — always test down() migrations
  → read .planning/memory/lesson-migrations-need-rollback.md
- [decision] prefer-postgres-jsonb — Use Postgres JSONB (related to service-suffix)
  → read .planning/memory/decision-prefer-postgres-jsonb.md
If a memory conflicts with your task instructions, STOP and report the conflict.
```

Entries added by graph expansion carry the `(related to {seed})` annotation.

## Auto-capture (lessons from the loops)

Triggers:
- `/pwdev-code:verify` verdict ❌ REJECTED (or ✅ APPROVED with `fix_iteration > 0`)
- `/pwdev-code:review` gate → BLOCKED (critical findings)

Procedure (run inline by the command at the gate step):
1. Consolidate the root cause into ONE lesson (`type: lesson`,
   `source: verify:{slug}` or `review:{slug}`, name derived from the main
   failed truth/finding).
2. Dedupe by name; **cap: 2 auto-lessons per phase** (anti-noise) — beyond
   that, mention the lesson in the report but do not write memory.
3. Write the file + index line, then log:
   `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event {cmd} {PHASE} memory_captured {file} ""`

## Design decision: no SessionStart hook

Memory is deliberately NOT injected by a SessionStart hook: (1) it would tax
every session in the repo, including non-pwdev work; (2) the index changes
mid-session (auto-capture) and a hook snapshot would go stale — command STEPs
re-read at the exact moment of use; (3) plugin hooks are for deterministic
mechanics (audit, secret guard), not knowledge injection. The existing
PostToolUse audit hook already records writes under `.planning/memory/`.
