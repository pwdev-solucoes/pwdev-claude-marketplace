---
description: Implements UI components based on the validated spec and configured stack (.planning/ui/stack.json). Checks gates before starting. Uses project-ui-skill when available.
argument-hint: "[component name or 'all']"
---

# /pwdev-uiux:build — Implement Component

**Argument**: $ARGUMENTS

## STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

## Check prerequisites

```bash
# UX spec gate
grep -q "\- \[x\]" .planning/ui/ux-spec.md 2>/dev/null && echo "UX OK" || echo "UX PENDING"

# Project UI Skill
ls .planning/ui/project-ui-skill.md 2>/dev/null && echo "Skill OK" || echo "No skill"
```

If ux-spec gate not approved:
> Run `/pwdev-uiux:analyze` first to create and approve the UX spec.

## Context for ui-builder

```
Required stack: [read from .planning/ui/stack.json — framework, library, forms, icons]

UX Spec: [content from ux-spec.md]
Figma Spec: [content from figma-spec.md if exists]
Project UI Skill: [content from project-ui-skill.md if exists]
Component: $ARGUMENTS

Implement with:
- All states: loading (Skeleton), empty (Empty), error (Alert), success (toast)
- Minimum accessibility: aria-label on icons, aria-live on dynamic elements
- Typed props with TypeScript (when available in the stack)
- Class prop for extensibility
- Register in .planning/ui/component-log.md upon completion
```

## Update phase

```
Current phase: PHASE 3 — Implement
```
