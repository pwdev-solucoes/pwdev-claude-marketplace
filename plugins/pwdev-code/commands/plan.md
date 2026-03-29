---
name: plan
description: Run the planning phase to break the spec into waves and executable tasks
---

# /pwdev-code:plan — Planning Phase

## Agent
Assume the persona of `.claude/agents/agent-planner.md`.

## References
Read: `CLAUDE.md` (section 6), `.planning/SPEC.md`, `.planning/phases/*-CONTEXT.md`.

## Skills
Read active skills from SPEC.md section 1 → reference them in tasks.

## Entry Gate
```bash
[ -f ".planning/SPEC.md" ] || { echo "❌ No SPEC.md. Run /pwdev-code:design first."; exit 1; }
```

## Flow

### STEP 1 — Absorb SPEC.md (silent)
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
Validate 100% SPEC.md coverage (objective, endpoints, tests, DoD).

### STEP 5 — Present and Wait for Approval
Show: N plans, N tasks, N waves, coverage N/N.

### STEP 6 — Save
- `.planning/phases/{NN}-{PP}-PLAN.md` (each plan)
- Update `.planning/STATE.md`: Phase PLAN ✅

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
