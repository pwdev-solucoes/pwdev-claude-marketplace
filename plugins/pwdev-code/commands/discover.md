---
description: Run the discovery phase to gather requirements through interviews and research
---

# /pwdev-code:discover — Discovery Phase

## Agent
Assume the persona of `.claude/agents/agent-interviewer.md`.
Spawn `.claude/agents/agent-researcher.md` in parallel (silent).

### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## References
Read: `CLAUDE.md` (sections 1-4), `.planning/state.md` (if it exists).

## Skills
If `.claude/skills/` has domain skills → load them for better questions.

## Entry Gate
Check if `.planning/` exists. If not → suggest `/pwdev-code:init` first.

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Codebase Mapping (silent, ~15s)
```bash
cat package.json composer.json requirements.txt 2>/dev/null | head -30
ls -la src/ app/ lib/ resources/ 2>/dev/null
cat .editorconfig tsconfig.json 2>/dev/null | head -20
ls tests/ test/ 2>/dev/null
cat .env.example 2>/dev/null | head -20
cat CLAUDE.md 2>/dev/null | head -50
```
DO NOT show raw output. Build a mental summary.

### STEP 2 — Greeting + Detected Context
Present: detected stack, requested feature.

### STEP 3 — Interview (agent-interviewer, 3 rounds)
Round 1: Scope and Objective
Round 2: Inputs and Rules
Round 3: Quality and Constraints
Wait for explicit confirmation between rounds if needed.

### STEP 4 — Parallel Research (agent-researcher)
Generate `.planning/context/` research files (domain.md, stack.md, pitfalls.md).

### STEP 5 — Synthesis and Confirmation
Present summary: scope, v1/v2 requirements, assumptions, risks, recommended level.
**Wait for explicit approval.**

### STEP 6 — Generate Artifacts
- `.planning/context/project.md`
- `.planning/context/requirements.md`
- `.planning/context/` (domain.md, stack.md, pitfalls.md)
- Update `.planning/state.md`: Phase DISCOVER ✅

### Transition
```
✅ Discovery complete.
📁 Artifacts in .planning/context/
👉 Next: /pwdev-code:design
```

## Prohibitions (command-level)
- ❌ NEVER generate code
- ❌ NEVER read .env (only .env.example)
- ❌ NEVER proceed without approval
