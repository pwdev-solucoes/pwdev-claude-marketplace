---
description: Run code review + QA test audit on implemented code. Spawns agent-code-reviewer and agent-qa in parallel.
argument-hint: "[files | --code-only | --tests-only | --diff HEAD~N]"
---

# /pwdev-code:review — Code Review + QA Audit

## Input
$ARGUMENTS: optional scope filter

| Argument | What it does |
|----------|-------------|
| *(empty)* | Review all changes since last commit (or staged changes) |
| `[file paths]` | Review specific files |
| `--code-only` | Run only code review (skip QA) |
| `--tests-only` | Run only QA test audit (skip code review) |
| `--diff HEAD~N` | Review last N commits |

---

## Entry Gate

```bash
# Verify there's code to review
git diff --name-only HEAD~1..HEAD 2>/dev/null || git diff --staged --name-only 2>/dev/null
```

If no changes found:
```
⚠️ No changes detected to review.
Specify files: /pwdev-code:review src/UserService.ts
Or a range:    /pwdev-code:review --diff HEAD~3
```

---

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Determine Scope

```bash
# Detect what to review
if [ -n "$ARGUMENTS" ]; then
  # Use provided scope
  FILES="$ARGUMENTS"
else
  # Default: changes from last commit or staged
  FILES=$(git diff --name-only HEAD~1..HEAD 2>/dev/null || git diff --staged --name-only)
fi

echo "Files to review:"
echo "$FILES"
echo "---"
echo "Total: $(echo "$FILES" | wc -l) files"
```

### STEP 2 — Load Context

```bash
# Read project conventions
cat CLAUDE.md 2>/dev/null | head -50
cat .planning/context/conventions.md 2>/dev/null | head -30
cat .planning/phases/{active-phase-slug}/spec.md 2>/dev/null | head -80
```

### STEP 3 — Spawn Agents

**If `--code-only`:** spawn only `agent-code-reviewer`
**If `--tests-only`:** spawn only `agent-qa`
**Default:** spawn both **in parallel**

#### Code Review Agent
```
Spawn: agent-code-reviewer
Scope: [file list]
Context:
  - spec.md sections 1, 5, 7 (persona, quality, prohibitions)
  - CLAUDE.md conventions
  - Active skills
Output: .planning/phases/{active-phase-slug}/review/code-review.md
```

#### QA Agent
```
Spawn: agent-qa
Scope: [file list]
Context:
  - spec.md sections 2, 5, 8 (objective, quality, DoD)
  - execution/*-summary.md files (what was implemented)
  - Active skills
Output: .planning/phases/{active-phase-slug}/review/qa-report.md
```

### STEP 4 — Consolidate Results

Wait for both agents to complete. Merge findings into a single summary.

### STEP 5 — Present Report

```
📋 Review Complete

## Code Review
  Verdict: [APPROVED | CHANGES REQUESTED | BLOCKED]
  Findings: [N] critical, [N] high, [N] medium, [N] low
  Report: .planning/phases/{active-phase-slug}/review/code-review.md

## QA Test Audit
  Verdict: [ADEQUATE | GAPS FOUND | INSUFFICIENT]
  Tests: [N] passed, [N] failed, [N] skipped
  Coverage gaps: [N] critical, [N] important
  Report: .planning/phases/{active-phase-slug}/review/qa-report.md

## Combined Verdict
  [PASS | FIX REQUIRED | BLOCKED]

## Action Items
  1. [highest priority fix]
  2. [next fix]
  ...

## Next Steps
  /pwdev-code:execute    → Fix reported issues
  /pwdev-code:verify     → Run full spec verification
  /pwdev-code:review     → Re-review after fixes
```

### STEP 6 — Update state.md

Record review results in `.planning/state.md`:
```markdown
## Last Review
- Date: [timestamp]
- Code Review: [verdict]
- QA: [verdict]
- Combined: [verdict]
- Open items: [N]
```

---

## Prohibitions
- NEVER fix code during review — only report findings
- NEVER skip the QA agent unless explicitly `--code-only`
- NEVER approve with critical security findings
- NEVER fabricate test results — run real commands
- NEVER review generated/build/vendor files
