---
description: Execute planned tasks by delegating to the executor agent
---

# /pwdev-code:execute — Execute Phase

## Agent
Assume the persona of `.claude/agents/agent-executor.md`.
Inject the stack/seniority from `.planning/SPEC.md` section 1 (Persona).

## Entry Gate
```bash
[ -f ".planning/SPEC.md" ] || { echo "❌ No SPEC.md. Run /pwdev-code:design first."; exit 1; }
ls .planning/phases/*-PLAN.md >/dev/null 2>&1 || { echo "❌ No PLAN.md. Run /pwdev-code:plan first."; exit 1; }
```

## Skills
Read SPEC.md section "Active Skills". For each skill:
```bash
cat .claude/skills/{name}/SKILL.md
```
Load BEFORE starting any task.

## Flow

### STEP 1 — Identify pending tasks
```bash
cat .planning/STATE.md
ls .planning/phases/*-PLAN.md
```
Determine: which plan, which task is next.

### STEP 2 — For each task:

**2.1** Load task from PLAN.md
**2.2** Deliver to agent-executor:
  - agent-executor.md (persona + rules)
  - SPEC.md sections 1, 6, 7
  - Active skills (each SKILL.md)
  - Task Markdown
  - "Required Context" files
**2.3** Agent executes: Setup → Implementation → Verification → Commit → Summary
**2.4** Collect SUMMARY.md
**2.5** If stop condition → report to the human, wait for decision

### STEP 3 — Persistence
After each task:
- Save `.planning/phases/{NN}-{PP}-SUMMARY.md`
- Update STATE.md (position + status)

After all tasks in a plan:
→ "Plan {PP} complete. Next plan or /pwdev-code:review?"

### STEP 4 — Transition
```
✅ Phase execution complete.
📁 Summaries in .planning/phases/
👉 Next: /pwdev-code:review (code review + QA audit)
   Then: /pwdev-code:verify (spec verification)
```

## Prohibitions (command-level, not agent-level)
- ❌ NEVER skip skill loading
- ❌ NEVER execute a task without an approved plan
- ❌ NEVER ignore a stop condition from the agent
- ❌ NEVER continue to verify without tasks completed or explicitly paused
