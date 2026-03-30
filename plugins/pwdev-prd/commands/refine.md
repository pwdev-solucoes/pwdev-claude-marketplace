---
description: Update an existing PRD through targeted questions about specific sections.
argument-hint: "[prd-slug]"
---

# /pwdev-prd:refine — Refine Existing PRD

## Agent
Assume the persona of `agents/agent-interviewer.md`.

## Input
$ARGUMENTS: PRD slug (required).

## Flow

### STEP 1 — Load existing PRD

```bash
PRD_DIR=".planning/prds/$ARGUMENTS"
if [ ! -f "$PRD_DIR/PRD.md" ]; then
  echo "❌ PRD not found: $PRD_DIR/PRD.md"
  echo "Available PRDs:"
  ls .planning/prds/ 2>/dev/null
  exit 1
fi
cat "$PRD_DIR/PRD.md"
```

### STEP 2 — Ask what to refine

```
I've loaded the PRD for "{slug}".

What would you like to refine?
1. Add or modify functional requirements
2. Update non-functional requirements
3. Revise architecture and approach
4. Add or update risks
5. Refine acceptance criteria
6. Update scope
7. Other (describe what you want to change)
```

### STEP 3 — Targeted Interview

Run only the relevant interview steps for the selected sections.
Follow the same rules: one question at a time, summarize, confirm.

### STEP 4 — Re-run Consistency Checks

Validate the entire PRD after changes.

### STEP 5 — Update PRD.md

Rewrite the complete PRD.md with the changes incorporated.
If prd.json exists, update it too.

### STEP 6 — Ask about commit

If changes were made:
```
PRD updated. Commit changes? (y/n)
```

If yes:
```bash
git add .planning/prds/{slug}/
git commit -m "docs(prd): update PRD for {slug}"
```

## Prohibitions
- NEVER lose existing content when refining
- NEVER skip consistency checks after changes
