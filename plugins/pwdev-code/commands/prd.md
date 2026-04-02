---
description: Create or refine a Product Requirements Document (PRD)
---

# /pwdev-code:prd — PRD Creation and Refinement

## Agent
Assume the persona of `.claude/agents/agent-prd.md`.

### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## References
If they exist, read before starting:
- `CLAUDE.md` — framework and conventions
- `.planning/context/project.md` — existing vision
- `.planning/product/roadmap/roadmap.md` — existing roadmap (if this is an update)

## Input
$ARGUMENTS: product/feature description (optional).

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Context Detection
```bash
cat .planning/context/project.md 2>/dev/null && echo "---PROJECT EXISTS---"
cat .planning/product/roadmap/roadmap.md 2>/dev/null && echo "---ROADMAP EXISTS---"
ls *.prd.md PRD.md prd.md 2>/dev/null && echo "---PRD EXISTS---"
```
If PRD exists → "Refine or create new?"

### STEP 2 — Product Interview (agent-prd, 3 rounds)
Round 1: Vision and Problem (4 questions)
Round 2: Scope and Features (4 questions)
Round 3: Constraints and Success (4 questions)

### STEP 3 — Generate PRD (10 sections)
1. Overview  2. Goals and Metrics  3. Functional Requirements (MoSCoW)
4. Non-Functional Requirements  5. Scope  6. User Stories with ACs
7. Technical Constraints  8. Risks  9. Timeline  10. Appendices

### STEP 4 — Internal Validation
PRD quality checklist (10 items).

### STEP 5 — Present and Wait for Approval

### STEP 6 — Persistence
```bash
cat > PRD.md << 'EOF'
[content]
EOF
cp PRD.md .planning/product/prd.md 2>/dev/null
```

### Transition
```
✅ PRD Generated → PRD.md
👉 Next: /pwdev-code:roadmap (executable roadmap) or /pwdev-code:discover (go direct)
```

## Prohibitions (command-level)
- ❌ NEVER generate code
- ❌ NEVER invent requirements without confirmation
- ❌ NEVER omit the scope section
- ❌ NEVER proceed without approval
