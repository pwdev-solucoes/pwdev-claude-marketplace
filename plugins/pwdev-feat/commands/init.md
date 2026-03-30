---
description: Initialize the pwdev-feat framework — creates .planning/feat/ workspace structure.
---

# /pwdev-feat:init — Initialize Framework

## STEP 1 — Check if already initialized

```bash
if [ -d ".planning/feat" ] && [ -d ".planning/feat/plans" ]; then
  echo "ALREADY_INITIALIZED"
else
  echo "NEW"
fi
```

If already initialized:
```
⚠️ pwdev-feat already initialized.
   Workspace: .planning/feat/
   Use /pwdev-feat:status to see current plans.
```
Stop here unless the user explicitly asks to reinitialize.

## STEP 2 — Detect project

```bash
# Detect stack
cat package.json 2>/dev/null | head -20
cat composer.json 2>/dev/null | head -20
cat requirements.txt 2>/dev/null | head -10
ls src/ app/ lib/ resources/ 2>/dev/null
cat CLAUDE.md 2>/dev/null | head -30
```

## STEP 3 — Create workspace

```bash
mkdir -p .planning/feat/plans
```

## STEP 4 — Summary

```
✅ pwdev-feat initialized

📁 Workspace created:
  .planning/feat/
  └── plans/          # Action plans will be stored here

📦 Detected stack: [stack info]

🚀 Next steps:
  /pwdev-feat:map-codebase  → Analyze existing codebase (recommended for existing projects)
  /pwdev-feat:setup         → Generate CLAUDE.md with project conventions
  /pwdev-feat:feat "desc"   → Create a feature plan
  /pwdev-feat:quick "desc"  → Quick task (no plan, direct execution)
```

## Prohibitions
- NEVER overwrite existing `.planning/feat/` without confirmation
- NEVER read .env files
