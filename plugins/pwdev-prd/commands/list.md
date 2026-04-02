---
description: List all PRDs in the workspace with status summary.
---

# /pwdev-prd:list — List PRDs

## STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

## Procedure

```bash
echo "=== PRDs ==="
for dir in .planning/prds/*/; do
  slug=$(basename "$dir")
  has_md=$([ -f "$dir/PRD.md" ] && echo "✅" || echo "❌")
  has_json=$([ -f "$dir/prd.json" ] && echo "✅" || echo "—")
  echo "$slug | MD: $has_md | JSON: $has_json"
done 2>/dev/null || echo "No PRDs found. Run /pwdev-prd:create to start."
```

Present:
```
📋 PRDs in .planning/prds/

| PRD | Markdown | JSON | Actions |
|-----|:--------:|:----:|---------|
| user-auth | ✅ | ✅ | /pwdev-prd:refine user-auth |
| inventory | ✅ | — | /pwdev-prd:refine inventory |

Total: {N} PRDs

👉 /pwdev-prd:create "desc"    → New PRD
👉 /pwdev-prd:refine {slug}    → Update existing
👉 /pwdev-prd:export {slug}    → Export to GitHub
```
