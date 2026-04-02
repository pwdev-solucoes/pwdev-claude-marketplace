---
description: Execute planned tasks by delegating to the executor agent
---

# /pwdev-code:execute — Execute Phase

## Agent
Assume the persona of `.claude/agents/agent-executor.md`.
Inject the stack/seniority from `.planning/phases/{active-phase-slug}/spec.md` section 1 (Persona).

### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## Entry Gate
```bash
[ -d ".planning/phases/" ] || { echo "❌ No phases folder. Run /pwdev-code:design first."; exit 1; }
ls .planning/phases/*/plans/*.md >/dev/null 2>&1 || { echo "❌ No plans found. Run /pwdev-code:plan first."; exit 1; }
```

## Skills
Read spec.md section "Active Skills". For each skill:
```bash
cat .claude/skills/{name}/SKILL.md
```
Load BEFORE starting any task.

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Identify pending tasks
```bash
cat .planning/state.md
ls .planning/phases/*/plans/*.md
```
Determine: which phase, which plan, which task is next.

### STEP 2 — For each task:

**2.1** Load task from the plan file in `.planning/phases/{active-phase-slug}/plans/`
**2.2** Deliver to agent-executor:
  - agent-executor.md (persona + rules)
  - spec.md sections 1, 6, 7
  - Active skills (each SKILL.md)
  - Task Markdown
  - "Required Context" files
**2.3** Agent executes: Setup → Implementation → Verification → Commit → Summary
**2.4** Collect summary
**2.5** If stop condition → report to the human, wait for decision

### STEP 3 — Persistence
After each task:
- Save `.planning/phases/{active-phase-slug}/execution/{PP}-summary.md`
- Update state.md (position + status)

After all tasks in a plan:
→ "Plan {PP} complete. Next plan or /pwdev-code:review?"

### STEP 4 — Transition
```
✅ Phase execution complete.
📁 Summaries in .planning/phases/{active-phase-slug}/execution/
👉 Next: /pwdev-code:review (code review + QA audit)
   Then: /pwdev-code:verify (spec verification)
```

## Prohibitions (command-level, not agent-level)
- ❌ NEVER skip skill loading
- ❌ NEVER execute a task without an approved plan
- ❌ NEVER ignore a stop condition from the agent
- ❌ NEVER continue to verify without tasks completed or explicitly paused
