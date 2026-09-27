---
type: feat-test-report
schema_version: 1
slug: {slug}
generated: {ISO-8601 timestamp}
verdict: {PASS|FAIL|BLOCKED}
---

# Test Report — {title}

## Coverage matrix
| Criterion / rule | Test IDs | Result | Evidence |
|------------------|----------|--------|----------|
| AC-001 | UNIT-001, INT-001, E2E-001 | {PASS|FAIL|NOT_RUN|NOT_APPLICABLE} | {path or excerpt} |

## Results by level
| Level | Command | Environment | Exit code | Result | Justification (if NOT_APPLICABLE) |
|-------|---------|-------------|-----------|--------|-----------------------------------|
| unit | | | | | never NOT_APPLICABLE |
| integration | | | | | |
| e2e (scenarios) | | | | | |
| e2e (playwright-cli) | | | | | |
| accessibility | | | | | |
| responsiveness | | | | | |

## E2E scenarios
| E2E id | File | ACs | Variants | Validation | Exported spec |
|--------|------|-----|----------|------------|---------------|

## Gaps and missing tests
| Gap | Proposed test ID | Level | Priority |
|-----|------------------|-------|----------|

## Tooling probes
| Tool | Probe | Result |
|------|-------|--------|
| playwright-cli | `command -v playwright-cli` | {available|missing} |

## Verdict
{PASS | FAIL | BLOCKED} — {one line}
