---
description: Generates complete handoff documentation for the implemented and approved UI components. Consolidates specs, findings and acceptance criteria.
---

# /pwdev-uiux:handoff

## STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

## Check review gate

```bash
grep "FAILED" .planning/ui/review-findings.md 2>/dev/null && echo "BLOCKED" || echo "OK"
```

If FAILED: `Fix the critical issues and run /pwdev-uiux:review again.`

## Generate document

Create `docs/handoff/[task-kebab]-[YYYY-MM-DD].md`:

```markdown
# Handoff — [Task]
**Date**: [date] | **Framework**: pwdev-uiux v2.0.0 | **Status**: APPROVED

## Stack used
[read from .planning/ui/stack.json — framework + library + forms]

## Problem solved
[from ux-spec]

## Delivered components

| Component | File | Library base (from stack.json) | States |
|---|---|---|---|
[from component-log]

## How to use the components

\`\`\`
[usage examples matching the configured stack]
\`\`\`

## Applied tokens
[from figma-spec]

## Acceptance criteria
[from ux-spec]

## Resolved review findings
[from review-findings — only the fixed ones]

## Improvement backlog
[from review-findings — medium and low severity]

## Development notes
[from component-log]
```

## Finalize flow

```bash
# Update state
cat > .planning/ui/current-flow.md << 'EOF'
# pwdev-uiux State
## Active flow
- Status: COMPLETED
- Handoff: docs/handoff/[file].md
EOF
```

```
✅ Handoff generated

File: docs/handoff/[file].md
pwdev-uiux flow completed.

→ /pwdev-uiux:start for next feature
→ /pwdev-uiux:scan to update the project skill
```
