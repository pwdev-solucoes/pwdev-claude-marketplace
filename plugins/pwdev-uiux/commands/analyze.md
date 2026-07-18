---
description: Quick UX + Figma analysis without starting a full flow. Activates ux-analyst and optionally design-bridge. Useful for exploration before committing to an implementation.
argument-hint: "[task description | Figma URL | both separated by space]"
---

# /pwdev-uiux:analyze

**Argument**: $ARGUMENTS

## STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

## Detect input type and spawn (real subagents, Task tool)

Prompts per `${CLAUDE_PLUGIN_ROOT}/references/spawn-contracts.md`; models per
`${CLAUDE_PLUGIN_ROOT}/references/model-profiles.md`.

If $ARGUMENTS contains a Figma URL (`figma.com`):
→ TWO Task calls in the SAME message (real parallelism):
  `pwdev-uiux:design-bridge` (MODE: READ, the URL) + `pwdev-uiux:ux-analyst`.

If $ARGUMENTS is a description only:
→ ONE Task call: `pwdev-uiux:ux-analyst`.

Read only the ≤10-line status replies; never paste the specs into your context.

## Expected result

- `.planning/ui/ux-spec.md` with approval gate
- `.planning/ui/figma-spec.md` (when Figma available)
- Summary presented to user with recommended next step
