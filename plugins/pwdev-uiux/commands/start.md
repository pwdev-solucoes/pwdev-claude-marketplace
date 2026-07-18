---
description: Starts a new UI/UX development flow using the configured stack. Activates the orchestrator and begins with UX analysis. Use with task description as argument.
argument-hint: "[UI task description, e.g.: 'create 3-step onboarding form']"
---

# /pwdev-uiux:start — Start New Flow

**Argument**: $ARGUMENTS

## STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

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

## Orchestrate (inline — you run in the MAIN context)

You are the orchestrator. Follow
`${CLAUDE_PLUGIN_ROOT}/references/workflow.md` end-to-end: it defines the
5 phases, their gates (which you verify with the human — that is why
orchestration runs inline), and the REAL subagent spawns per phase via the
Task tool with prompts from
`${CLAUDE_PLUGIN_ROOT}/references/spawn-contracts.md` and models from
`${CLAUDE_PLUGIN_ROOT}/references/model-profiles.md`.

Start PHASE 1 now: spawn `pwdev-uiux:ux-analyst` with the task
`$ARGUMENTS`, the stack from `.planning/ui/stack.json`, the skill paths, and
`LANGUAGE: {lang}`. Wait for its status reply, present the spec to the human,
and only advance to PHASE 2 after the gate is approved.

## Inform user

```
🚀 pwdev-uiux v2.0.0 — Flow started

Task: $ARGUMENTS
Phase: PHASE 1 — Understand
Subagent: pwdev-uiux:ux-analyst

Use /pwdev-uiux:status to track progress.
```
