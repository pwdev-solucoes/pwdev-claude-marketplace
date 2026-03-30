---
description: Generate CHANGELOG.md from commits, summaries, and verifications
---

# /pwdev-code:changelog — Changelog Generator

## Role
Utility agent that generates CHANGELOG.md from commits, summaries, and
PWDEV-CODE verifications. Follows the [Keep a Changelog](https://keepachangelog.com/) standard.

## Input
- $ARGUMENTS: version (e.g.: "1.0.0") or "auto" (detects from latest tag)
- If empty, uses "Unreleased"

## Procedure

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
ls .planning/phases/*-SUMMARY.md 2>/dev/null
ls .planning/phases/*-VERIFY.md 2>/dev/null
ls .planning/quick/*/SUMMARY.md 2>/dev/null
```

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
- Verdict: [result from latest VERIFY.md]
```

Save to `CHANGELOG.md` (append at the top if it already exists).

## Prohibitions
- ❌ NEVER fabricate commits (read from real git log)
- ❌ NEVER overwrite existing changelog (append/merge)
- ❌ NEVER include hashes of reverted commits without a note
