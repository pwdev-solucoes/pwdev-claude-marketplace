---
description: Update an existing PRD through targeted questions about specific sections.
argument-hint: "[prd-slug]"
---

# /pwdev-prd:refine — Refine Existing PRD

## Agent
Assume the persona of `agents/agent-interviewer.md`.

## Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## Input
$ARGUMENTS: PRD slug (required).

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

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
