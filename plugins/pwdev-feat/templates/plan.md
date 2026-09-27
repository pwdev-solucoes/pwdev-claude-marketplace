---
type: feat-plan
schema_version: 3
slug: {slug}
plan_type: {feature|backend|frontend|test|review}
status: pending
created: {ISO-8601 timestamp}
---

# Action Plan — {title}

> **Type:** {feature|backend|frontend|test|review}
> **Created:** {timestamp}
> **Status:** pending

(Review plans — and report-only plans whose Output Format lists only files under `.planning/` —
run in REPORT mode: findings only, no commit.)

---

## 1. Persona & Scope
**Persona:** {who the executor should be}
**Scope:** {exact boundaries}
**Stack:** {technologies and versions}
**UI:** {yes|no}

## 2. Direct Objective
{what must exist when done — 1-3 clear sentences}

## 3. Minimum Inputs
### Entities / Data
{fields, types, relationships}
### Business Rules
{validations, constraints, edge cases — BR-001, BR-002 ...}
### Existing Files to Read
- `{path}` — {why}

## 4. Output Format
| File | Action | Description |
|------|--------|-------------|
| `{path}` | create | {what} |

## 5. Quality Criteria
| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-001 | {verifiable criterion} | `{command}` / UNIT-001 / playwright-cli: {check} / E2E-001 |

## 6. Ambiguity Handling
**Assumptions made:**
- {assumption and why}
**If unsure during execution:**
- {instruction}

## 7. Prohibitions
- {specific prohibition}

---

## Risks
- {risk} — {mitigation}

## Execution Steps
1. {concrete step} — files: `{path}` — covers: AC-001

## Verification
| Command | Purpose |
|---------|---------|
| `{command}` | {lint / unit / integration / e2e / build} |

## Done
{single sentence defining "finished"}

## Commit
`{type}({scope}): {description}`
