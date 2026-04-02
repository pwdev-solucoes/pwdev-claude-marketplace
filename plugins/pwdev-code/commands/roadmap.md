---
description: Decomposes PRD into an executable multi-file roadmap with traceability. Generates .planning/product/roadmap/ structure.
---

# /pwdev-code:roadmap — PRD → Executable Roadmap

## Agent
Assume the persona of `agents/agent-roadmap.md`.

### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## References
Read: `CLAUDE.md` (sections 1-4, 10), `.planning/context/project.md`, `.planning/state.md`.

## Input
PRD in 3 formats: inline, file path, or "use existing requirements.md".
If $ARGUMENTS contains a path → read it. If empty → ask for PRD.

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 0.1 — Validate PRD
Completeness checklist (10 elements). If >=3 missing → flag.

### STEP 1 — Analysis and Decomposition
Hierarchy: Phase → Epic → Feature → Task.
Numbering: F01-E01-FT01-T01.
Prioritize: technical dependencies > value > risk.

### STEP 2 — Generate Multi-File Structure
```
.planning/product/roadmap/
├── roadmap.md, traceability.md, risks.md, metrics.md, rollout.md, validation.md
├── F01-slug/ (PHASE.md, CHECKLIST-F01.md, F01-E01-slug/ (EPIC.md, features...))
```

### STEP 3 — Present Summary
N phases, N epics, N features, N tasks, N files.
Prioritization decisions. **Await approval.**

### STEP 4 — Generate Files
```bash
mkdir -p .planning/product/roadmap/F01-slug/F01-E01-slug
# [generate all files]
```

### STEP 5 — Integrate with .planning/
```bash
# roadmap.md is already at .planning/product/roadmap/roadmap.md
echo "✅ Roadmap generated"
```

### Transition
```
✅ Roadmap generated: [N] files in .planning/product/roadmap/
👉 Next: /pwdev-code:discover (first feature from Phase 1)
```

## Prohibitions
- NEVER generate code
- NEVER create feature without acceptance criteria
- NEVER omit traceability.md
- NEVER proceed without approval after summary
