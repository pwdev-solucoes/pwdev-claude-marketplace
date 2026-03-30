---
description: Generate specialized checklists for different stages of the development cycle
---

# /pwdev-code:checklist — Checklist Generator

## Role
Utility agent that generates specialized checklists for different stages
of the development cycle.

## Input
$ARGUMENTS: checklist type. Available types:
- `preflight` — before starting a feature (prerequisites)
- `release` — before deploy/merge (quality)
- `security` — security audit
- `review` — code review checklist
- `onboard` — onboarding a new dev to the project

If empty, ask which type.

## Procedure

Read the project context:
```bash
cat CLAUDE.md 2>/dev/null | head -100
cat .planning/SPEC.md 2>/dev/null | head -50
cat .planning/PROJECT.md 2>/dev/null | head -30
cat package.json 2>/dev/null | head -20
cat composer.json 2>/dev/null | head -20
```

Generate the checklist adapted to the stack and project context.

### Type: preflight

```markdown
# ✈️ Pre-Flight Checklist — [Feature]

## Environment
- [ ] Branch created from develop: `feature/[name]`
- [ ] Deps updated: `[npm install | composer install]`
- [ ] .env configured (copy from .env.example)
- [ ] Database running and migrations executed
- [ ] Existing tests pass before starting

## PWDEV-CODE
- [ ] /pwdev-code:discover complete → PROJECT.md + REQUIREMENTS.md
- [ ] /pwdev-code:design complete → SPEC.md approved
- [ ] /pwdev-code:plan complete → PLANs approved
- [ ] STATE.md updated

## Scope
- [ ] Scope defined and documented in SPEC.md
- [ ] "Out of scope" explicit
- [ ] Acceptance criteria verifiable
- [ ] Stop conditions defined
```

### Type: release

```markdown
# 🚀 Release Checklist — [version]

## Quality
- [ ] Lint with no errors: `[command]`
- [ ] Type-check with no errors: `[command]`
- [ ] Unit tests pass: `[command]`
- [ ] Feature/integration tests pass: `[command]`
- [ ] E2E tests pass: `[command]` (if there is UI)
- [ ] Coverage ≥ [X%]

## Security
- [ ] `[npm audit | composer audit]` with no critical/high vulnerabilities
- [ ] No hardcoded secrets (grep scan)
- [ ] .env not committed
- [ ] CORS configured correctly
- [ ] Rate limiting active

## Code
- [ ] Code review approved
- [ ] No blocking TODO/FIXME
- [ ] No console.log/dd() in production
- [ ] Error handling on all endpoints

## Delivery
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Reversible migrations (if applicable)
- [ ] Version tag created
- [ ] VERIFY.md with ✅ verdict

## Deploy
- [ ] Environment variables configured in production
- [ ] Rollback plan documented
- [ ] Monitoring/alerts configured
```

### Type: security

```markdown
# 🔒 Security Checklist

## Authentication
- [ ] Passwords hashed (bcrypt/argon2)
- [ ] JWT with reasonable expiration
- [ ] Refresh token in httpOnly cookie
- [ ] Rate limiting on login/register
- [ ] Brute force protection

## Authorization
- [ ] RBAC/ABAC implemented
- [ ] Auth middleware on protected routes
- [ ] Ownership verification on resources

## Data
- [ ] Input validated (server-side, not just client)
- [ ] SQL injection protected (prepared statements/ORM)
- [ ] XSS protected (output sanitization)
- [ ] CSRF protection active
- [ ] Sensitive data encrypted at rest

## Infrastructure
- [ ] HTTPS mandatory
- [ ] Security headers (CSP, HSTS, X-Frame-Options)
- [ ] Restrictive CORS
- [ ] Secrets in environment variables (not code)
- [ ] .env in .gitignore
- [ ] Stack traces not exposed in production

## Dependencies
- [ ] npm audit / composer audit clean
- [ ] No deprecated lib with known CVE
```

### Type: review

```markdown
# 👀 Code Review Checklist

## Functionality
- [ ] Code does what the task asks (no more, no less)
- [ ] Edge cases handled
- [ ] Adequate error handling
- [ ] Follows SPEC.md acceptance criteria

## Quality
- [ ] Readable code (clear names, small functions)
- [ ] No unnecessary duplication
- [ ] Complete typing (no unjustified `any`)
- [ ] Follows project conventions

## Security
- [ ] No hardcoded secrets
- [ ] Input validated
- [ ] Output sanitized (if UI)

## Tests
- [ ] New tests cover the new code
- [ ] Existing tests still pass
- [ ] Error scenarios tested

## Process
- [ ] Commit messages follow Conventional Commits
- [ ] Only in-scope files were changed
- [ ] No generated/build files committed
```

### Type: onboard

```markdown
# 🎒 Onboarding Checklist — [Project]

## Setup
- [ ] Clone repo: `git clone [url]`
- [ ] Install deps: `[npm install | composer install]`
- [ ] Copy .env: `cp .env.example .env`
- [ ] Configure local database
- [ ] Run migrations: `[command]`
- [ ] Run seeds: `[command]`
- [ ] Verify tests: `[command]`

## Understand the Project
- [ ] Read CLAUDE.md (PWDEV-CODE framework)
- [ ] Read .planning/PROJECT.md (vision and stack)
- [ ] Read .planning/SPEC.md (current contract)
- [ ] Read .planning/roadmap/ROADMAP.md (what is planned)
- [ ] Browse folder structure (~15min)

## Tools
- [ ] IDE configured with [recommended extensions]
- [ ] Lint/formatter configured
- [ ] Docker running (if applicable)
- [ ] Repo access (push)
- [ ] Board/issues access

## First Commit
- [ ] Pick a Quick task from .planning/
- [ ] Execute: `/pwdev-code:quick "[simple task]"`
- [ ] Open PR and request review
```

Save the generated checklist to `.planning/checklists/[type]-[date].md`.

## Prohibitions
- ❌ NEVER generate a generic checklist without reading the project context
- ❌ NEVER omit the security section in a release checklist
- ❌ NEVER include commands without verifying they exist in the project
