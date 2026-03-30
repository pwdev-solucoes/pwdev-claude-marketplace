---
description: Archive artifacts from completed phases and keep .planning/ organized
---

# /pwdev-code:cleanup — Artifact Cleanup

## Role
Utility agent that archives artifacts from completed phases and keeps
`.planning/` organized.

## Procedure

### STEP 1 — Inventory

```bash
echo "=== PHASES ==="
ls -la .planning/phases/ 2>/dev/null

echo "=== QUICK ==="
ls -la .planning/quick/ 2>/dev/null

echo "=== RESEARCH ==="
ls -la .planning/research/ 2>/dev/null

echo "=== STATE ==="
cat .planning/STATE.md 2>/dev/null

echo "=== SIZE ==="
du -sh .planning/ 2>/dev/null
```

### STEP 2 — Identify Archivable Items

Rules:
- Phases with VERIFY.md ✅ APPROVED → can be archived
- Quick tasks with SUMMARY.md ✅ → can be archived
- Research/ → keep (may be consulted in the future)
- STATE.md → NEVER archive
- SPEC.md → NEVER archive (it is the active contract)

### STEP 3 — Ask the Human

```markdown
## 🧹 Archivable Artifacts

| Artifact | Size | Status | Suggested action |
|----------|------|:------:|------------------|
| phases/01-*.md | [X]KB | ✅ Phase complete | Archive |
| quick/001-*/ | [X]KB | ✅ Complete | Archive |
| research/ | [X]KB | 📚 Reference | Keep |

**Action:** Move archivable items to `.planning/archive/[date]/`

Confirm? (y/n)
```

### STEP 4 — Execute (after approval)

```bash
ARCHIVE_DIR=".planning/archive/$(date +%Y-%m-%d)"
mkdir -p "$ARCHIVE_DIR"

# Move completed phases
mv .planning/phases/01-* "$ARCHIVE_DIR/" 2>/dev/null

# Move completed quick tasks
mv .planning/quick/001-* "$ARCHIVE_DIR/" 2>/dev/null

echo "✅ Archived to $ARCHIVE_DIR"
```

## Prohibitions
- ❌ NEVER delete artifacts (only move to archive/)
- ❌ NEVER archive STATE.md, SPEC.md, PROJECT.md, REQUIREMENTS.md
- ❌ NEVER execute without human confirmation
- ❌ NEVER archive a phase without an approved VERIFY.md
