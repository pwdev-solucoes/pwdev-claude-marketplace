---
description: Starts a new Vue UI/UX development flow. Activates the orchestrator and begins with UX analysis. Use with task description as argument.
argument-hint: "[UI task description, e.g.: 'create 3-step onboarding form']"
---

# /pwdev-uiux:start — Start New Flow

**Argument**: $ARGUMENTS

## STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

## Pre-check

```bash
# Check for active flow
grep -q "in progress" .planning/ui/current-flow.md 2>/dev/null && echo "ACTIVE" || echo "FREE"
```

If flow active: ask the user whether to continue or cancel.

## Check project-ui-skill

```bash
# Project skill available?
wc -l .planning/ui/project-ui-skill.md 2>/dev/null || echo "Skill not found"
```

If skill missing and project has components:
> Tip: run `/pwdev-uiux:scan` first so the ui-builder builds consistently with the existing project.

## Clear previous state

```bash
printf "# UX Spec\n*Pending*\n" > .planning/ui/ux-spec.md
printf "# Figma Spec\n*Pending*\n" > .planning/ui/figma-spec.md
printf "# Review Findings\n*Pending*\n" > .planning/ui/review-findings.md
```

## Register start

Update `.planning/ui/current-flow.md`:
```markdown
# pwdev-uiux State

## Active flow
- **Task**: $ARGUMENTS
- **Status**: in progress
- **Phase**: PHASE 1 — Understand
- **Pending gate**: ux-spec approved
- **Started**: [timestamp]
```

## Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## Activate orchestrator

Invoke `orchestrator` with:
```
New task started via /pwdev-uiux:start:

Task: $ARGUMENTS
Stack: [read from .planning/ui/stack.json — framework, library, forms]

Project UI Skill available: [yes/no — include content if yes]

Start PHASE 1: spawn ux-analyst to create spec in .planning/ui/ux-spec.md
Wait for approval gate before advancing to PHASE 2.
```

## Inform user

```
🚀 pwdev-uiux v1.0.0 — Flow started

Task: $ARGUMENTS
Phase: PHASE 1 — Understand
Agent: ux-analyst

The ux-analyst is analyzing the context and creating the UX spec.
Use /pwdev-uiux:status to track progress.
```
