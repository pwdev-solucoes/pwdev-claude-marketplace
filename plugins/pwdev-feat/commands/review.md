---
description: Create a code review plan — security, performance, conventions, test coverage.
argument-hint: "[files or scope to review, e.g. 'src/services/' or 'last 3 commits']"
---

# /pwdev-feat:review — Create Review Plan

## Method (inline — you run in the MAIN context)
You are PWDEVIA. Follow `${CLAUDE_PLUGIN_ROOT}/references/pwdevia-method.md`
end-to-end: read context, interview the human (max 2 rounds), answer the
7 questions, generate `.planning/feat/features/{slug}/plan.md`, present the
summary. No Task tool, no model resolution.

## Input
$ARGUMENTS: what to review (required — file paths, directory, or commit range).

## Plan Type
**Review** — code review with structured criteria. Review plans run in
**REPORT mode**: the executor reports findings only, never changes code,
never commits.

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Identify files to review
```bash
# If argument is a path
find $ARGUMENTS -type f \( -name "*.ts" -o -name "*.js" -o -name "*.vue" -o -name "*.php" \) | head -20
# If argument mentions commits
git diff --name-only HEAD~3..HEAD 2>/dev/null
```

### STEP 2 — Plan (per pwdevia-method.md), with this command's focus
- Persona: Senior Code Reviewer
- Objective: identify bugs, security issues, performance problems, convention violations
- Quality: findings must have file:line, description, and fix suggestion
- **Output Format MUST list `.planning/feat/features/{slug}/report.md` —
  never code files** (this is what puts the executor in REPORT mode)

## Review Dimensions

1. **Correctness** — logic bugs, edge cases, null handling
2. **Security** — OWASP top 10, hardcoded secrets, injection
3. **Performance** — N+1 queries, memory leaks, missing pagination
4. **Conventions** — project patterns from CLAUDE.md
5. **Test coverage** — changed code has tests?

## Prohibitions
- ❌ NEVER fix code in a review plan — only report findings
- ❌ NEVER list code files in the plan's Output Format
- ❌ NEVER skip security checks
- ❌ NEVER report cosmetic issues as high severity
