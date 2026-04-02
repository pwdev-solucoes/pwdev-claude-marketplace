---
description: Quick UX + Figma analysis without starting a full flow. Activates ux-analyst and optionally design-bridge. Useful for exploration before committing to an implementation.
argument-hint: "[task description | Figma URL | both separated by space]"
---

# /pwdev-uiux:analyze

**Argument**: $ARGUMENTS

## STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

## Detect input type

If $ARGUMENTS contains Figma URL (`figma.com`):
→ Spawn `design-bridge` with URL + `ux-analyst` in parallel

If $ARGUMENTS is description only:
→ Spawn `ux-analyst` only

## Expected result

- `.planning/ui/ux-spec.md` with approval gate
- `.planning/ui/figma-spec.md` (when Figma available)
- Summary presented to user with recommended next step
