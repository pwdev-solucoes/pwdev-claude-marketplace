---
description: Create a PRD or decompose it into an executable roadmap
argument-hint: "[prd [description] | roadmap [path]]"
---

# /pwdev-code:product — Product Planning

## Role
Product planning utility: creates PRDs through structured interviews or decomposes them into executable multi-file roadmaps with traceability.

## Input
$ARGUMENTS: subcommand + optional arguments.
- `prd` → create or refine a PRD (interactive interview)
- `prd <description>` → create PRD with initial context
- `roadmap` → generate roadmap from existing PRD/requirements
- `roadmap <path>` → generate roadmap from a specific PRD file
- empty → show interactive menu

---

## Procedure

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Route Subcommand

Parse $ARGUMENTS:

- **`prd`** or **`prd <description>`** → go to STEP 2
- **`roadmap`** or **`roadmap <path>`** → go to STEP 3
- **empty** → present menu:

  **PT-BR:**
  ```
  Planejamento de Produto

  1. prd      — Criar ou refinar um PRD (Product Requirements Document)
  2. roadmap  — Gerar roadmap executavel a partir do PRD

  Escolha (1-2):
  ```

  **EN:**
  ```
  Product Planning

  1. prd      — Create or refine a PRD (Product Requirements Document)
  2. roadmap  — Generate executable roadmap from PRD

  Choose (1-2):
  ```

---

## STEP 2 — PRD Creation and Refinement

### Agent
Assume the persona of `.claude/agents/agent-prd.md`.

### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

### References
If they exist, read before starting:
- `CLAUDE.md` — framework and conventions
- `.planning/context/project.md` — existing vision
- `.planning/product/roadmap/roadmap.md` — existing roadmap (if this is an update)

### STEP 2.1 — Context Detection
```bash
cat .planning/context/project.md 2>/dev/null && echo "---PROJECT EXISTS---"
cat .planning/product/roadmap/roadmap.md 2>/dev/null && echo "---ROADMAP EXISTS---"
ls *.prd.md PRD.md prd.md 2>/dev/null && echo "---PRD EXISTS---"
```
If PRD exists → "Refine or create new?"

### STEP 2.2 — Product Interview (agent-prd, 3 rounds)
Round 1: Vision and Problem (4 questions)
Round 2: Scope and Features (4 questions)
Round 3: Constraints and Success (4 questions)

### STEP 2.3 — Generate PRD (10 sections)
1. Overview  2. Goals and Metrics  3. Functional Requirements (MoSCoW)
4. Non-Functional Requirements  5. Scope  6. User Stories with ACs
7. Technical Constraints  8. Risks  9. Timeline  10. Appendices

### STEP 2.4 — Internal Validation
PRD quality checklist (10 items).

### STEP 2.5 — Present and Wait for Approval

### STEP 2.6 — Persistence
```bash
cat > PRD.md << 'EOF'
[content]
EOF
cp PRD.md .planning/product/prd.md 2>/dev/null
```

### Transition
```
✅ PRD Generated → PRD.md
👉 Next: /pwdev-code:product roadmap (executable roadmap) or /pwdev-code:discover (go direct)
```

### PRD Prohibitions
- ❌ NEVER generate code
- ❌ NEVER invent requirements without confirmation
- ❌ NEVER omit the scope section
- ❌ NEVER proceed without approval

---

## STEP 3 — PRD → Executable Roadmap

### Agent
Assume the persona of `agents/agent-roadmap.md`.

### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

### References
Read: `CLAUDE.md` (sections 1-4, 10), `.planning/context/project.md`, `.planning/state.md`.

### Input
PRD in 3 formats: inline, file path, or "use existing requirements.md".
If $ARGUMENTS contains a path after `roadmap` → read it. If only `roadmap` → look for existing PRD.

### STEP 3.0.1 — Validate PRD
Completeness checklist (10 elements). If >=3 missing → flag.

### STEP 3.1 — Analysis and Decomposition
Hierarchy: Phase → Epic → Feature → Task.
Numbering: F01-E01-FT01-T01.
Prioritize: technical dependencies > value > risk.

### STEP 3.2 — Generate Multi-File Structure
```
.planning/product/roadmap/
├── roadmap.md, traceability.md, risks.md, metrics.md, rollout.md, validation.md
├── F01-slug/ (PHASE.md, CHECKLIST-F01.md, F01-E01-slug/ (EPIC.md, features...))
```

### STEP 3.3 — Present Summary
N phases, N epics, N features, N tasks, N files.
Prioritization decisions. **Await approval.**

### STEP 3.4 — Generate Files
```bash
mkdir -p .planning/product/roadmap/F01-slug/F01-E01-slug
# [generate all files]
```

### STEP 3.5 — Integrate with .planning/
```bash
# roadmap.md is already at .planning/product/roadmap/roadmap.md
echo "✅ Roadmap generated"
```

### Transition
```
✅ Roadmap generated: [N] files in .planning/product/roadmap/
👉 Next: /pwdev-code:discover (first feature from Phase 1)
```

### Roadmap Prohibitions
- NEVER generate code
- NEVER create feature without acceptance criteria
- NEVER omit traceability.md
- NEVER proceed without approval after summary
