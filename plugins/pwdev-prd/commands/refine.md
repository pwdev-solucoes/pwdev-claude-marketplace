---
description: Update an existing PRD through targeted questions about specific sections.
argument-hint: "[prd-slug]"
---

# /pwdev-prd:refine — Refine Existing PRD

## Method (inline — you run in the MAIN context)
You are the PRD interviewer. Follow
`${CLAUDE_PLUGIN_ROOT}/references/interview-method.md` (persona, principles,
consistency checks). No Task tool, no model resolution — you interview the
human.

## Input
$ARGUMENTS: PRD slug (required).

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Load existing PRD

```bash
PRD_DIR=".planning/prds/$ARGUMENTS"
if [ ! -f "$PRD_DIR/PRD.md" ]; then
  echo "PRD_NOT_FOUND"
  ls .planning/prds/ 2>/dev/null
else
  cat "$PRD_DIR/PRD.md"
fi
```

If `PRD_NOT_FOUND` → show the available slugs and STOP.

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
If prd.json exists, update it too (canonical structure in
`${CLAUDE_PLUGIN_ROOT}/references/interview-method.md`).
Log: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event refine "" completed ".planning/prds/{slug}/PRD.md" ""`

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
