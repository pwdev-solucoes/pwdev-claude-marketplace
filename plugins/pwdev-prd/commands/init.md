---
name: init
description: Initialize the pwdev-prd framework — creates .planning/prds/ workspace.
---

# /pwdev-prd:init — Initialize PRD Workspace

## STEP 1 — Check if already initialized

```bash
if [ -d ".planning/prds" ]; then
  echo "ALREADY_INITIALIZED"
  ls .planning/prds/ 2>/dev/null
else
  echo "NEW"
fi
```

If already initialized:
```
⚠️ pwdev-prd already initialized.
   Workspace: .planning/prds/
   Existing PRDs: [list]
   Use /pwdev-prd:create to start a new PRD.
```

## STEP 2 — Create workspace

```bash
mkdir -p .planning/prds
```

## STEP 3 — Summary

```
✅ pwdev-prd initialized

📁 Workspace created:
  .planning/prds/           # PRDs will be stored here
    └── {slug}/
        ├── PRD.md           # Structured PRD document
        └── prd.json         # Optional JSON export

🚀 Next steps:
  /pwdev-prd:create "feature or system description"
  /pwdev-prd:list                → View existing PRDs
```

## Prohibitions
- NEVER overwrite existing `.planning/prds/` without confirmation
