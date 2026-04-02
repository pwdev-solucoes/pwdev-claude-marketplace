---
description: Archive artifacts from completed phases and keep .planning/ organized
---

# /pwdev-code:cleanup — Artifact Cleanup

## Role
Utility agent that archives artifacts from completed phases and keeps
`.planning/` organized.

## Procedure

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Inventory

```bash
echo "=== PHASES ==="
ls -la .planning/phases/ 2>/dev/null

echo "=== QUICK ==="
ls -la .planning/quick/ 2>/dev/null

echo "=== CONTEXT ==="
ls -la .planning/context/ 2>/dev/null

echo "=== STATE ==="
cat .planning/state.md 2>/dev/null

echo "=== SIZE ==="
du -sh .planning/ 2>/dev/null
```

### STEP 2 — Identify Archivable Items

Rules:
- Phase folders with verify/verify.md ✅ APPROVED → can be archived
- Quick tasks with summary.md ✅ → can be archived
- context/ → keep (may be consulted in the future)
- state.md → NEVER archive
- Active phase spec.md → NEVER archive (it is the active contract)

### STEP 3 — Ask the Human

```markdown
## 🧹 Archivable Artifacts

| Artifact | Size | Status | Suggested action |
|----------|------|:------:|------------------|
| phases/{phase-slug}/ | [X]KB | ✅ Phase complete | Archive |
| quick/{slug}/ | [X]KB | ✅ Complete | Archive |
| context/ | [X]KB | 📚 Reference | Keep |

**Action:** Move archivable items to `.planning/archive/[date]/`

Confirm? (y/n)
```

### STEP 4 — Execute (after approval)

```bash
ARCHIVE_DIR=".planning/archive/$(date +%Y-%m-%d)"
mkdir -p "$ARCHIVE_DIR"

# Move completed phase folders
mv .planning/phases/{phase-slug}/ "$ARCHIVE_DIR/" 2>/dev/null

# Move completed quick tasks
mv .planning/quick/{slug}/ "$ARCHIVE_DIR/" 2>/dev/null

echo "✅ Archived to $ARCHIVE_DIR"
```

## Prohibitions
- ❌ NEVER delete artifacts (only move to archive/)
- ❌ NEVER archive state.md, active spec.md, project.md, requirements.md
- ❌ NEVER execute without human confirmation
- ❌ NEVER archive a phase without an approved verify.md
