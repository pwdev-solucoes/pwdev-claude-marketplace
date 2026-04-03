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

### STEP 0.5 — Stale Session Detection & Context Refresh

Automatically detect if the session is stale and generate fresh context for the executor subagent.

```bash
# Check last activity timestamp
LAST_COMMIT=$(git log -1 --format="%ct" 2>/dev/null || echo "0")
LAST_SUMMARY=$(stat -c "%Y" .planning/phases/*/execution/*-summary.md 2>/dev/null | sort -n | tail -1 || echo "0")
LAST_ACTIVITY=$(( LAST_COMMIT > LAST_SUMMARY ? LAST_COMMIT : LAST_SUMMARY ))
NOW=$(date +%s)
IDLE_HOURS=$(( (NOW - LAST_ACTIVITY) / 3600 ))

# Check for uncommitted changes
git status --short 2>/dev/null
grep -rl "Status: in progress" .planning/phases/*/execution/*.md 2>/dev/null
```

**If IDLE_HOURS > 2** (stale session detected), generate context automatically:

1. Read `.planning/state.md` — current position
2. Read active `spec.md` sections 1, 6, 7 (persona, stop conditions, prohibitions)
3. Run `git log --oneline -10` and `git diff --name-only HEAD~5` — recent changes
4. Read last `execution/*-summary.md` — what was done last
5. Extract active decisions from `decisions.md` relevant to the next task

Generate `.planning/phases/{active-phase-slug}/execution/executor-context.md`:

```markdown
# Executor Context — Phase [{phase-slug}]

> Auto-generated on: [date] (idle for ~[N] hours)

## Current State
- Plan: [PP] of [total]
- Task: [TT] of [total]
- Last completed task: [ID] — [status]

## Persona (from spec.md)
[copy section 1 in full]

## Active Prohibitions (from spec.md)
[copy section 7 in full]

## Active Stop Conditions (from spec.md)
[copy section 6 in full]

## Recently Modified Files
[git diff --name-only from recent tasks]

## Decisions in Effect
[only decisions relevant to the next task]

## Alerts
- [if there was a deviation in the last task]
- [if there is a pending fix plan]
- [if there is a blocked dependency]
- [if uncommitted code exists — warn]
```

If uncommitted code is detected → warn the human:
- PT-BR: `⚠️ Codigo nao commitado detectado. Deseja commitar antes de continuar? (s/n)`
- EN: `⚠️ Uncommitted code detected. Commit before continuing? (y/n)`

**If IDLE_HOURS <= 2** → skip context generation, proceed normally.

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
