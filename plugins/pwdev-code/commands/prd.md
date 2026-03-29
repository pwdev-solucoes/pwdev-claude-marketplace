---
name: prd
description: Create or refine a Product Requirements Document (PRD)
---

# /pwdev-code:prd — PRD Creation and Refinement

## Agent
Assume the persona of `.claude/agents/agent-prd.md`.

## References
If they exist, read before starting:
- `CLAUDE.md` — framework and conventions
- `.planning/PROJECT.md` — existing vision
- `.planning/roadmap/ROADMAP.md` — existing roadmap (if this is an update)

## Input
$ARGUMENTS: product/feature description (optional).

## Flow

### STEP 1 — Context Detection
```bash
cat .planning/PROJECT.md 2>/dev/null && echo "---PROJECT EXISTS---"
cat .planning/roadmap/ROADMAP.md 2>/dev/null && echo "---ROADMAP EXISTS---"
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
cp PRD.md .planning/PRD.md 2>/dev/null
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
