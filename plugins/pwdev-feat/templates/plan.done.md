<!-- feat-status: {COMPLETE|CAVEATS|FAILED} -->
# Execution Report — {plan title}

> **Plan:** {slug}
> **Executed:** {ISO-8601 timestamp}
> **Mode:** {IMPLEMENT|REPORT} — {subagent|inline} on {runtime}
> **Base commit:** {sha}
> **Status:** {✅ COMPLETE | ⚠️ WITH CAVEATS | ❌ FAILED}

## What Was Done
| File | Action | Description |
|------|--------|-------------|

## Acceptance Criteria
| ID | Result | Command / check | Exit code | Evidence |
|----|--------|-----------------|-----------|----------|
| AC-001 | PASS | `{command}` | 0 | {one-line real output or evidence path} |
| AC-004 | PASS | playwright-cli: {check} | 0 | evidence/AC-004-happy_path.png — {observed state} |

## E2E
| Scenario | Validate (exit) | Exported spec | Committed |
|----------|-----------------|---------------|-----------|

## Planned vs. Changed Files
| File | Planned | Changed |
|------|---------|---------|

## Verification
| Command | Exit code | Result |
|---------|-----------|--------|

## Deviations from Plan
- {deviation — or "None"}

## Commit
- Hash: {hash | none}
- Message: {message}
- Files: {list}
{REPORT mode: "none — findings at report.md"}
