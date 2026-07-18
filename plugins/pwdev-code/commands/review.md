---
description: Run code review + QA test audit on implemented code. Spawns the code-reviewer and qa subagents in parallel.
argument-hint: "[files | --code-only | --tests-only | --diff HEAD~N]"
---

# /pwdev-code:review — Code Review + QA Audit

## Role (orchestrator — the subagents review; you consolidate)

## Input
$ARGUMENTS: optional scope filter

| Argument | What it does |
|----------|-------------|
| *(empty)* | Review all changes since last commit (or staged changes) |
| `[file paths]` | Review specific files |
| `--code-only` | Run only code review (skip QA) |
| `--tests-only` | Run only QA test audit (skip code review) |
| `--diff HEAD~N` | Review last N commits |

## Entry Gate

```bash
git diff --name-only HEAD~1..HEAD 2>/dev/null || git diff --staged --name-only 2>/dev/null
```

If no changes found:
```
⚠️ No changes detected to review.
Specify files: /pwdev-code:review src/UserService.ts
Or a range:    /pwdev-code:review --diff HEAD~3
```

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Determine Scope

```bash
if [ -n "$ARGUMENTS" ]; then
  FILES="$ARGUMENTS"
else
  FILES=$(git diff --name-only HEAD~1..HEAD 2>/dev/null || git diff --staged --name-only)
fi
echo "$FILES"
```

### STEP 2 — Gather Spawn Inputs
Read (for the prompts only — do not analyze yourself):
`.planning/phases/{active-phase-slug}/spec.md` sections 1, 2, 5, 7, 8;
paths of `execution/*-summary.md`; active skills list.

### STEP 3 — Spawn Subagents (REAL parallelism)

**Default:** issue BOTH Task tool calls in a SINGLE message so they run in
parallel. `--code-only` → only code-reviewer; `--tests-only` → only qa.
Resolve each `model` per `${CLAUDE_PLUGIN_ROOT}/references/model-profiles.md`.

1. `subagent_type: "pwdev-code:code-reviewer"` — prompt from the
   **code-reviewer** template in
   `${CLAUDE_PLUGIN_ROOT}/references/spawn-contracts.md`
   (scope = file list/diff range, spec §1/5/7, conventions pointer, skills,
   `LANGUAGE: {lang}`).
   Writes: `review/code-review.md`.
2. `subagent_type: "pwdev-code:qa"` — prompt from the **qa** template
   (spec §2/5/8, summary paths, skills, `LANGUAGE: {lang}`).
   Writes: `review/qa-report.md`.

### STEP 4 — Consolidate Results
Wait for both status replies (≤10 lines each). Read ONLY the replies — do
not paste the report files into your context.

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
  ...

## Next Steps
  /pwdev-code:execute    → Fix reported issues
  /pwdev-code:verify     → Run full spec verification
  /pwdev-code:review     → Re-review after fixes
```

### STEP 6 — Review Gate + state.md

Record in `.planning/state.md`:
```markdown
## Last Review
- Date: [timestamp]
- Code Review: [verdict]
- QA: [verdict]
- Combined: [verdict]
- Open items: [N]
- review_gate: [OK | BLOCKED]
```

**Gate rule:** if critical findings > 0 (either report) → `review_gate: BLOCKED`.
While BLOCKED, `/pwdev-code:verify` refuses to run — fix the findings via
`/pwdev-code:execute` and re-review, or the human explicitly overrides.
Log it: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event review REVIEW gate_rejected review '{"critical":N}'`
(or `gate_passed` when OK).

## Prohibitions
- ❌ NEVER fix code during review — only report findings
- ❌ NEVER review the code yourself — spawn the subagents
- ❌ NEVER skip the qa subagent unless explicitly `--code-only`
- ❌ NEVER approve with critical security findings
- ❌ NEVER paste report files into your context — status replies only
- ❌ NEVER review generated/build/vendor files
