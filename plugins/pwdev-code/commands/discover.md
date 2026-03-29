---
name: discover
description: Run the discovery phase to gather requirements through interviews and research
---

# /pwdev-code:discover — Discovery Phase

## Agent
Assume the persona of `.claude/agents/agent-interviewer.md`.
Spawn `.claude/agents/agent-researcher.md` in parallel (silent).

## References
Read: `CLAUDE.md` (sections 1-4), `.planning/STATE.md` (if it exists).

## Skills
If `.claude/skills/` has domain skills → load them for better questions.

## Entry Gate
Check if `.planning/` exists. If not → suggest `/pwdev-code:init` first.

## Flow

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
Generate `.planning/research/` (domain.md, stack.md, pitfalls.md).

### STEP 5 — Synthesis and Confirmation
Present summary: scope, v1/v2 requirements, assumptions, risks, recommended level.
**Wait for explicit approval.**

### STEP 6 — Generate Artifacts
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/research/` (3 files)
- Update `.planning/STATE.md`: Phase DISCOVER ✅

### Transition
```
✅ Discovery complete.
📁 Artifacts in .planning/
👉 Next: /pwdev-code:design
```

## Prohibitions (command-level)
- ❌ NEVER generate code
- ❌ NEVER read .env (only .env.example)
- ❌ NEVER proceed without approval
