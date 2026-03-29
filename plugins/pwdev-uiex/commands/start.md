---
name: pwdev-start
description: Starts a new Vue UI/UX development flow. Activates the orchestrator and begins with UX analysis. Use with task description as argument.
argument-hint: "[UI task description, e.g.: 'create 3-step onboarding form']"
---

# /pwdev-uiex:start — Start New Flow

**Argument**: $ARGUMENTS

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
> Tip: run `/pwdev-uiex:scan` first so the ui-builder builds consistently with the existing project.

## Clear previous state

```bash
printf "# UX Spec\n*Pending*\n" > .planning/ui/ux-spec.md
printf "# Figma Spec\n*Pending*\n" > .planning/ui/figma-spec.md
printf "# Review Findings\n*Pending*\n" > .planning/ui/review-findings.md
```

## Register start

Update `.planning/ui/current-flow.md`:
```markdown
# pwdev-uiex State

## Active flow
- **Task**: $ARGUMENTS
- **Status**: in progress
- **Phase**: PHASE 1 — Understand
- **Pending gate**: ux-spec approved
- **Started**: [timestamp]
```

## Activate orchestrator

Invoke `orchestrator` with:
```
New task started via /pwdev-uiex:start:

Task: $ARGUMENTS
Stack: [read from .planning/ui/stack.json — framework, library, forms]

Project UI Skill available: [yes/no — include content if yes]

Start PHASE 1: spawn ux-analyst to create spec in .planning/ui/ux-spec.md
Wait for approval gate before advancing to PHASE 2.
```

## Inform user

```
🚀 pwdev-uiex v1.0.0 — Flow started

Task: $ARGUMENTS
Phase: PHASE 1 — Understand
Agent: ux-analyst

The ux-analyst is analyzing the context and creating the UX spec.
Use /pwdev-uiex:status to track progress.
```
