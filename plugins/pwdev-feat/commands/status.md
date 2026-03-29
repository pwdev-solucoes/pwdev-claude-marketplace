---
name: status
description: Show current plans — pending, executed, and failed.
---

# /pwdev-feat:status — Plan Status

## Procedure

```bash
echo "=== PENDING PLANS ==="
ls .planning/feat/plans/*.md 2>/dev/null | grep -v ".done.md" | sort

echo "=== EXECUTED PLANS ==="
ls .planning/feat/plans/*.done.md 2>/dev/null | sort

echo "=== CODEBASE CONTEXT ==="
[ -f ".planning/feat/codebase.md" ] && echo "✅ codebase.md present" || echo "⚠️ No codebase.md — run /pwdev-feat:map-codebase"

echo "=== CLAUDE.MD ==="
[ -f "CLAUDE.md" ] && echo "✅ CLAUDE.md present" || echo "⚠️ No CLAUDE.md — run /pwdev-feat:setup"
```

Present:
```
📊 pwdev-feat Status

Pending plans: {N}
Executed plans: {N}
Codebase context: {present / missing}
CLAUDE.md: {present / missing}

Pending:
  001-user-crud.md         → /pwdev-feat:exec 001
  002-auth-tests.md        → /pwdev-feat:exec 002

Executed:
  003-login-page.done.md   → ✅ COMPLETE

👉 Next: /pwdev-feat:exec {next pending number}
```
