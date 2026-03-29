---
name: roadmap
description: Decomposes PRD into an executable multi-file roadmap with traceability. Generates .planning/roadmap/ structure.
---

# /pwdev-code:roadmap — PRD → Executable Roadmap

## Agent
Assume the persona of `agents/agent-roadmap.md`.

## References
Read: `CLAUDE.md` (sections 1-4, 10), `.planning/PROJECT.md`, `.planning/STATE.md`.

## Input
PRD in 3 formats: inline, file path, or "use existing REQUIREMENTS.md".
If $ARGUMENTS contains a path → read it. If empty → ask for PRD.

## Flow

### STEP 0 — Validate PRD
Completeness checklist (10 elements). If >=3 missing → flag.

### STEP 1 — Analysis and Decomposition
Hierarchy: Phase → Epic → Feature → Task.
Numbering: F01-E01-FT01-T01.
Prioritize: technical dependencies > value > risk.

### STEP 2 — Generate Multi-File Structure
```
.planning/roadmap/
├── ROADMAP.md, TRACEABILITY.md, RISKS.md, METRICS.md, ROLLOUT.md, VALIDATION.md
├── F01-slug/ (PHASE.md, CHECKLIST-F01.md, F01-E01-slug/ (EPIC.md, features...))
```

### STEP 3 — Present Summary
N phases, N epics, N features, N tasks, N files.
Prioritization decisions. **Await approval.**

### STEP 4 — Generate Files
```bash
mkdir -p .planning/roadmap/F01-slug/F01-E01-slug
# [generate all files]
```

### STEP 5 — Integrate with .planning/
```bash
cp .planning/roadmap/ROADMAP.md .planning/ROADMAP.md 2>/dev/null
```

### Transition
```
✅ Roadmap generated: [N] files in .planning/roadmap/
👉 Next: /pwdev-code:discover (first feature from Phase 1)
```

## Prohibitions
- NEVER generate code
- NEVER create feature without acceptance criteria
- NEVER omit TRACEABILITY.md
- NEVER proceed without approval after summary
