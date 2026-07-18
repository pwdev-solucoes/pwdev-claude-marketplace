---
description: Implements UI components based on the validated spec and configured stack (.planning/ui/stack.json). Checks gates before starting. Uses project-ui-skill when available.
argument-hint: "[component name or 'all']"
---

# /pwdev-uiux:build — Implement Component

**Argument**: $ARGUMENTS

## STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

## Check prerequisites

```bash
# UX spec gate
grep -q "\- \[x\]" .planning/ui/ux-spec.md 2>/dev/null && echo "UX OK" || echo "UX PENDING"

# Project UI Skill
ls .planning/ui/project-ui-skill.md 2>/dev/null && echo "Skill OK" || echo "No skill"
```

If ux-spec gate not approved:
> Run `/pwdev-uiux:analyze` first to create and approve the UX spec.

## Spawn the ui-builder (real subagent, Task tool)

- `subagent_type`: `pwdev-uiux:ui-builder`
- `model`: resolve per `${CLAUDE_PLUGIN_ROOT}/references/model-profiles.md`
  (override key `uiux-ui-builder`)
- prompt per `${CLAUDE_PLUGIN_ROOT}/references/spawn-contracts.md`:

```
TASK: implement component(s): $ARGUMENTS
STACK: {path .planning/ui/stack.json — read it yourself}
SKILLS — read these files BEFORE working:
  ${CLAUDE_PLUGIN_ROOT}/skills/ui-best-practices/SKILL.md
  ${CLAUDE_PLUGIN_ROOT}/skills/ui-theme-reference/SKILL.md
  ${CLAUDE_PLUGIN_ROOT}/skills/ux-tokens/SKILL.md
  {+ every skill listed in stack.json skills[]}
ARTIFACTS TO READ: .planning/ui/ux-spec.md, .planning/ui/figma-spec.md (if
exists), .planning/ui/project-ui-skill.md (if exists)
LANGUAGE: {lang}

OUTPUT CONTRACT:
1. Implement with ALL states (loading/empty/error/success), a11y minimums,
   typed props, class prop; register each component in
   .planning/ui/component-log.md.
2. Reply with AT MOST 10 lines: STATUS, components registered, NOTE.
```

Read only the status reply.

## Update phase

```
Current phase: PHASE 3 — Implement
```
