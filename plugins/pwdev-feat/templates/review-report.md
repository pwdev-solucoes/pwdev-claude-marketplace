---
type: feat-review-report
schema_version: 1
slug: {slug}
base: {base ref or sha}
target: {target ref or sha}
verdict: {APPROVED|CHANGES_REQUESTED}
generated: {ISO-8601 timestamp}
---

# Code Review — {title}

## Scope
- Range: `{base}..{target}`
- Changed files: {N} (see `review/changed-files.txt`)
- Package: `.planning/feat/features/{slug}/review/`
- Scope status: {CONFIRMED|AMBIGUOUS — stopped}

## Rules consulted
| Source | Path |
|--------|------|
| Project instructions | {path} |
| Conventions | .planning/feat/context/conventions.md |
| Plan under review | {path or n/a} |

## Findings
| finding_id | severity | location | rule | evidence | suggestion |
|------------|----------|----------|------|----------|------------|
| CR-001 | {BLOCKER|HIGH|MEDIUM|LOW|INFO} | `{path}:{line}` | {rule citation} | {evidence} | {fix} |

## Summary by dimension
| Dimension | Findings | Highest severity |
|-----------|----------|------------------|
| Correctness | | |
| Security | | |
| Performance | | |
| Conventions | | |
| Tests | | |

## Verification commands
| Command | Exit code | Result |
|---------|-----------|--------|

## Verdict
{APPROVED | CHANGES_REQUESTED} — {one line}

## Fix scope (when CHANGES_REQUESTED)
| finding_id | Files |
|------------|-------|
