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

## Index format — `MEMORY.md`

One line per ACTIVE memory, fixed grammar (nothing else in the file body):

```markdown
# Project Memory Index
<!-- managed by /pwdev-code:memory — one line per ACTIVE memory; edit via the command -->

- `decision` prefer-postgres-jsonb — Use Postgres JSONB for flexible fields (memory/decision-prefer-postgres-jsonb.md)
- `lesson` migrations-need-rollback — Verify rejected user-auth: always test down() migrations (memory/lesson-migrations-need-rollback.md)
- `convention` service-suffix — Services end in *Service under app/Services (memory/convention-service-suffix.md)
```

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
2. Select **≤5** entries by keyword overlap between each line's name/description
   and the task scope (file paths, domain terms, phase slug).
3. Priority by consumer:
   - executor / code-reviewer / simplifier → `convention` first
   - verifier → `lesson` first
   - design (main context) → `decision` + `convention`
4. No match → **omit the block entirely** (never inject an empty section).

## RELEVANT MEMORY block (canonical template)

Inject paths, not pasted content — the subagent reads only what it needs:

```
RELEVANT MEMORY — curated project knowledge; treat as binding constraints:
- [convention] service-suffix — Services end in *Service under app/Services
  → read .planning/memory/convention-service-suffix.md
- [lesson] migrations-need-rollback — always test down() migrations
  → read .planning/memory/lesson-migrations-need-rollback.md
If a memory conflicts with your task instructions, STOP and report the conflict.
```

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
