---
name: pwdev-analyze
description: Quick UX + Figma analysis without starting a full flow. Activates ux-analyst and optionally design-bridge. Useful for exploration before committing to an implementation.
argument-hint: "[task description | Figma URL | both separated by space]"
---

# /pwdev-uiex:analyze

**Argument**: $ARGUMENTS

## Detect input type

If $ARGUMENTS contains Figma URL (`figma.com`):
→ Spawn `design-bridge` with URL + `ux-analyst` in parallel

If $ARGUMENTS is description only:
→ Spawn `ux-analyst` only

## Expected result

- `.planning/ui/ux-spec.md` with approval gate
- `.planning/ui/figma-spec.md` (when Figma available)
- Summary presented to user with recommended next step
