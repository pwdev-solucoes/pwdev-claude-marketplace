---
description: Export a PRD as a GitHub issue or regenerate the JSON export.
argument-hint: "[prd-slug] [--json | --github]"
---

# /pwdev-prd:export — Export PRD

## Input
$ARGUMENTS: `{slug} --json` or `{slug} --github` or just `{slug}` (interactive).

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Load PRD

```bash
SLUG=$(echo "$ARGUMENTS" | awk '{print $1}')
PRD_DIR=".planning/prds/$SLUG"
[ -f "$PRD_DIR/PRD.md" ] && cat "$PRD_DIR/PRD.md" || { echo "PRD_NOT_FOUND"; ls .planning/prds/ 2>/dev/null; }
```

If `PRD_NOT_FOUND` → show the available slugs and STOP.

### STEP 2 — Determine export type

If `--json` → generate/update prd.json
If `--github` → create GitHub issue
If neither → ask:

```
Export PRD "{slug}" as:
1. JSON file (.planning/prds/{slug}/prd.json)
2. GitHub issue
3. Both
```

### Mode: JSON Export

Generate `.planning/prds/{slug}/prd.json` following the canonical JSON
structure in `${CLAUDE_PLUGIN_ROOT}/references/interview-method.md`:

- Keys in English
- Values in the PRD language (as written)
- No empty fields
- No sections that don't appear in the PRD

### Mode: GitHub Issue

```bash
gh issue create \
  --title "PRD: {feature name}" \
  --body "$(cat .planning/prds/{slug}/PRD.md)" \
  --label "prd,documentation"
```

If `gh` is not available:
```
⚠️ GitHub CLI (gh) not found.
   Install: https://cli.github.com/
   Or copy the PRD from: .planning/prds/{slug}/PRD.md
```

### STEP 3 — Summary

```
✅ PRD exported

Format: {JSON / GitHub Issue / Both}
Files: {list of files created/updated}
GitHub: {issue URL if created}
```

## Prohibitions
- NEVER push to GitHub without asking
- NEVER modify the original PRD.md during export
