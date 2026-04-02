---
description: Show current features — pending, executed, and failed.
---

# /pwdev-feat:status — Feature Status

## STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

## Procedure

```bash
echo "=== PENDING FEATURES ==="
for dir in .planning/feat/features/*/; do
  slug=$(basename "$dir")
  [ -f "$dir/plan.md" ] && [ ! -f "$dir/plan.done.md" ] && echo "$slug"
done 2>/dev/null

echo "=== EXECUTED FEATURES ==="
for dir in .planning/feat/features/*/; do
  slug=$(basename "$dir")
  [ -f "$dir/plan.done.md" ] && echo "$slug"
done 2>/dev/null

echo "=== CODEBASE CONTEXT ==="
[ -f ".planning/feat/codebase.md" ] && echo "✅ codebase.md present" || echo "⚠️ No codebase.md — run /pwdev-feat:map-codebase"

echo "=== CLAUDE.MD ==="
[ -f "CLAUDE.md" ] && echo "✅ CLAUDE.md present" || echo "⚠️ No CLAUDE.md — run /pwdev-feat:setup"
```

Present:
```
📊 pwdev-feat Status

Pending features: {N}
Executed features: {N}
Codebase context: {present / missing}
CLAUDE.md: {present / missing}

Pending:
  user-crud       → /pwdev-feat:exec user-crud
  auth-tests      → /pwdev-feat:exec auth-tests

Executed:
  login-page      → ✅ COMPLETE

👉 Next: /pwdev-feat:exec {next pending slug}
```
