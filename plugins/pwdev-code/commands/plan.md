---
description: Run the planning phase to break the spec into waves and executable tasks
---

# /pwdev-code:plan — Planning Phase

## Agent
Assume the persona of `.claude/agents/agent-planner.md`.

### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## References
Read: `CLAUDE.md` (section 6), `.planning/phases/{active-phase-slug}/spec.md`, `.planning/phases/{active-phase-slug}/decisions.md`.

## Skills
Read active skills from spec.md section 1 → reference them in tasks.

## Entry Gate
```bash
# Read state.md to find the active phase slug
cat .planning/state.md 2>/dev/null || { echo "❌ No state.md. Run /pwdev-code:init first."; exit 1; }
# Verify spec.md exists in the active phase folder
ls .planning/phases/*/spec.md >/dev/null 2>&1 || { echo "❌ No spec.md. Run /pwdev-code:design first."; exit 1; }
```

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Absorb spec.md (silent)
Read from `.planning/phases/{active-phase-slug}/spec.md`.
Extract: Persona (1), Objective (2), Inputs (3), Quality (5),
Stop conditions (6), Prohibitions (7), DoD (8).

### STEP 2 — Define Waves
Organize into waves (parallel vs sequential).
**Present wave map. Wait for approval.**

### STEP 3 — Generate Task Markdown
For each Plan, generate tasks in the standard format from CLAUDE.md section 6.
Maximum 3 tasks per plan, 5 files per task, 7 actions per task.
Include active skills in "Required Context" when relevant.

### STEP 4 — Coverage Checklist
Validate 100% spec.md coverage (objective, endpoints, tests, DoD).

### STEP 5 — Present and Wait for Approval
Show: N plans, N tasks, N waves, coverage N/N.

### STEP 6 — Save
- `.planning/phases/{active-phase-slug}/plans/{PP}-{task-slug}.md` (each plan)
- Update `.planning/state.md`: Phase PLAN ✅

### Transition
```
✅ Planning complete.
📋 [N] plans, [N] tasks, [N] waves
👉 Next: /pwdev-code:execute
```

## Prohibitions (command-level)
- ❌ NEVER generate code
- ❌ NEVER create a task with >5 files or a plan with >3 tasks
- ❌ NEVER proceed without approval
