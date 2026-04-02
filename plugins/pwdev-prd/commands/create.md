---
description: Start a structured interview to create a new PRD. Produces Markdown + optional JSON.
argument-hint: "[feature or system description]"
---

# /pwdev-prd:create — Create New PRD

## Agent
Assume the persona of `agents/agent-interviewer.md`.

## Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## Input
$ARGUMENTS: brief description of the feature or system (required).

## Pre-check

```bash
mkdir -p .planning/prds
```

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Determine PRD slug

From $ARGUMENTS, generate a kebab-case slug (e.g., "user-authentication", "inventory-management").

Create directory:
```bash
mkdir -p .planning/prds/{slug}
```

### STEP 2 — Start Interview

Follow the 12-step interview process from agent-interviewer.md:

1. Context and overview
2. Problem and opportunity
3. Objectives and success metrics
4. Scope
5. Functional requirements
6. Non-functional requirements
7. Architecture and approach
8. Decisions and trade-offs
9. Dependencies
10. Risks and mitigation
11. Acceptance criteria
12. Testing and validation

**Rules:**
- One question at a time
- Summarize at end of each step
- Confirm before moving on
- Mark unknowns as hypothesis

### STEP 3 — Consistency Checks

Before generating, run all consistency checks from agent-interviewer.md.
Flag any issues and resolve with the user.

### STEP 4 — Generate PRD.md

Write to `.planning/prds/{slug}/PRD.md` following exactly the template in `templates/PRD.template.md`.

### STEP 5 — Ask about JSON export

```
The PRD has been generated in Markdown.

Would you also like a JSON export with English keys? (y/n)
```

If yes → generate `.planning/prds/{slug}/prd.json` following the JSON structure from agent-interviewer.md.

### STEP 6 — Ask about commit

```
📋 PRD created: .planning/prds/{slug}/PRD.md

Would you like to commit this PRD to the repository? (y/n)
```

If yes:
```bash
git add .planning/prds/{slug}/
git commit -m "docs(prd): add PRD for {slug}"
```

### STEP 7 — Summary

```
✅ PRD created

📄 Files:
  .planning/prds/{slug}/PRD.md      ← Structured PRD
  .planning/prds/{slug}/prd.json    ← JSON export (if requested)

📊 Summary:
  Product: {product}
  Feature: {feature}
  Functional requirements: {N}
  Non-functional requirements: {N}
  Risks: {N}
  Acceptance criteria: {N}

👉 Next:
  /pwdev-prd:refine {slug}     → Update this PRD
  /pwdev-prd:export {slug}     → Export to GitHub issue
  /pwdev-feat:feat             → Create action plan from this PRD (if pwdev-feat installed)
  /pwdev-code:discover         → Start full workflow from this PRD (if pwdev-code installed)
```

## Prohibitions
- NEVER skip the interview — always ask questions
- NEVER invent requirements the user didn't provide
- NEVER include specific technology choices (PRDs are technology-agnostic)
- NEVER commit without asking
