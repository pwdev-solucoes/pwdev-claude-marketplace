---
description: Show current features — pending, executed, with caveats, and failed.
disable-model-invocation: true
allowed-tools: Read, Bash
---

# /pwdev-feat:status — Feature Status

## STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

## Procedure

```bash
for dir in .planning/feat/features/*/; do
  [ -f "${dir}plan.md" ] || continue
  slug=$(basename "$dir")
  if [ ! -f "${dir}plan.done.md" ]; then
    echo "PENDING $slug"
  else
    st=$(grep -m1 -oE 'FAILED|WITH CAVEATS|COMPLETE' "${dir}plan.done.md")
    echo "${st:-EXECUTED} $slug"
  fi
done 2>/dev/null

echo "=== CODEBASE CONTEXT ==="
[ -f ".planning/feat/codebase.md" ] && echo "✅ codebase.md present" || echo "⚠️ No codebase.md — run /pwdev-feat:map-codebase"

echo "=== CLAUDE.MD ==="
[ -f "CLAUDE.md" ] && echo "✅ CLAUDE.md present" || echo "⚠️ No CLAUDE.md — run /pwdev-feat:setup"
```

Present:
```
📊 pwdev-feat Status

Pending: {N} | Complete: {N} | With caveats: {N} | Failed: {N}
Codebase context: {present / missing}
CLAUDE.md: {present / missing}

Pending:
  user-crud       → /pwdev-feat:exec user-crud

Complete:
  login-page      → ✅

With caveats:
  profile-page    → ⚠️ see .planning/feat/features/profile-page/plan.done.md

Failed:
  auth-tests      → ❌ re-run: /pwdev-feat:exec auth-tests

👉 Next: /pwdev-feat:exec {next pending slug}
```
