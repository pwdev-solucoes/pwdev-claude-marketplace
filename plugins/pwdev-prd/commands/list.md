---
description: List all PRDs in the workspace with status summary.
---

# /pwdev-prd:list — List PRDs

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
