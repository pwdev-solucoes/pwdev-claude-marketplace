---
description: Project maintenance — archive completed artifacts or generate changelog
argument-hint: "[cleanup | changelog [version]]"
---

# /pwdev-code:maintenance — Project Maintenance

## Role
Utility agent for project housekeeping: archiving completed phase artifacts and generating changelogs from commit history.

## Input
$ARGUMENTS: subcommand + optional arguments.
- `cleanup` → archive completed phase artifacts
- `changelog` → generate CHANGELOG.md (version auto-detected)
- `changelog 1.0.0` → generate CHANGELOG.md for a specific version
- empty → show interactive menu

## Procedure

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Route Subcommand

Parse $ARGUMENTS:

- **`cleanup`** → go to STEP 2
- **`changelog`** or **`changelog <version>`** → go to STEP 3
- **empty** → present menu:

  **PT-BR:**
  ```
  Manutencao do Projeto

  1. cleanup    — Arquivar artefatos de fases concluidas
  2. changelog  — Gerar CHANGELOG.md a partir dos commits

  Escolha (1-2):
  ```

  **EN:**
  ```
  Project Maintenance

  1. cleanup    — Archive completed phase artifacts
  2. changelog  — Generate CHANGELOG.md from commits

  Choose (1-2):
  ```

---

## STEP 2 — Artifact Cleanup

### STEP 2.1 — Inventory

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

### STEP 2.2 — Identify Archivable Items

Rules:
- Phase folders with verify/verify.md ✅ APPROVED → can be archived
- Quick tasks with summary.md ✅ → can be archived
- context/ → keep (may be consulted in the future)
- state.md → NEVER archive
- Active phase spec.md → NEVER archive (it is the active contract)

### STEP 2.3 — Ask the Human

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

### STEP 2.4 — Execute (after approval)

```bash
ARCHIVE_DIR=".planning/archive/$(date +%Y-%m-%d)"
mkdir -p "$ARCHIVE_DIR"

# Move completed phase folders
mv .planning/phases/{phase-slug}/ "$ARCHIVE_DIR/" 2>/dev/null

# Move completed quick tasks
mv .planning/quick/{slug}/ "$ARCHIVE_DIR/" 2>/dev/null

echo "✅ Archived to $ARCHIVE_DIR"
```

### Cleanup Prohibitions
- ❌ NEVER delete artifacts (only move to archive/)
- ❌ NEVER archive state.md, active spec.md, project.md, requirements.md
- ❌ NEVER execute without human confirmation
- ❌ NEVER archive a phase without an approved verify.md

---

## STEP 3 — Changelog Generator

Follows the [Keep a Changelog](https://keepachangelog.com/) standard.

### Input
Version from $ARGUMENTS after `changelog` (e.g.: "1.0.0") or "auto" (detects from latest tag).
If empty, uses "Unreleased".

### STEP 3.1 — Collect Data

```bash
# 1. Detect latest tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
VERSION="${ARGUMENTS:-Unreleased}"

# 2. Collect commits since latest tag
if [ -n "$LAST_TAG" ]; then
  COMMITS=$(git log ${LAST_TAG}..HEAD --pretty=format:"%h|%s|%an|%ai" --no-merges)
else
  COMMITS=$(git log --pretty=format:"%h|%s|%an|%ai" --no-merges)
fi

# 3. Collect summaries (real evidence)
ls .planning/phases/*/execution/*-summary.md 2>/dev/null
ls .planning/phases/*/verify/verify.md 2>/dev/null
ls .planning/quick/*/summary.md 2>/dev/null
```

### STEP 3.2 — Generate Changelog

Categorize commits by type (Conventional Commits):

```markdown
# Changelog

## [VERSION] — [date]

### ✨ Added (feat)
- [human-readable description of what was added] ([hash])

### 🐛 Fixed (fix)
- [description] ([hash])

### ♻️ Refactored (refactor)
- [description] ([hash])

### 🧪 Tests (test)
- [description] ([hash])

### 📝 Documentation (docs)
- [description] ([hash])

### 🔧 Maintenance (chore)
- [description] ([hash])

### ⚡ Performance (perf)
- [description] ([hash])

---

### Verification
- Verified phases: [list]
- Verdict: [result from latest verify.md]
```

Save to `CHANGELOG.md` (append at the top if it already exists).

### Changelog Prohibitions
- ❌ NEVER fabricate commits (read from real git log)
- ❌ NEVER overwrite existing changelog (append/merge)
- ❌ NEVER include hashes of reverted commits without a note
