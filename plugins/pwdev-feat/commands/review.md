---
description: Create a code review plan — security, performance, conventions, test coverage.
argument-hint: "[files or scope to review, e.g. 'src/services/' or 'last 3 commits']"
---

# /pwdev-feat:review — Create Review Plan

## Agent
Assume the persona of `agents/agent-planner.md` (PWDEVIA).

## Input
$ARGUMENTS: what to review (required — file paths, directory, or commit range).

## Plan Type
**Review** — code review with structured criteria.

## Flow

1. Read context: CLAUDE.md + .planning/feat/codebase.md
2. Identify files to review:
   ```bash
   # If argument is a path
   find $ARGUMENTS -type f \( -name "*.ts" -o -name "*.js" -o -name "*.vue" -o -name "*.php" \) | head -20
   # If argument mentions commits
   git diff --name-only HEAD~3..HEAD 2>/dev/null
   ```
3. Apply the 7 fundamental questions with review focus:
   - Persona: Senior Code Reviewer
   - Objective: identify bugs, security issues, performance problems, convention violations
   - Quality: findings must have file:line, description, and fix suggestion
   - Output: review report (not code fixes)
4. Generate plan in `.planning/feat/plans/{NNN}-{slug}.md`
5. Present summary with next step: `/pwdev-feat:exec {NNN}`

## Review Dimensions

1. **Correctness** — logic bugs, edge cases, null handling
2. **Security** — OWASP top 10, hardcoded secrets, injection
3. **Performance** — N+1 queries, memory leaks, missing pagination
4. **Conventions** — project patterns from CLAUDE.md
5. **Test coverage** — changed code has tests?

## Prohibitions
- NEVER fix code in a review plan — only report findings
- NEVER skip security checks
- NEVER report cosmetic issues as high severity
