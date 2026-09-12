# PWDEV QA workflow contract

This contract defines status evaluation and workflow boundaries shared by every PWDEV QA skill.
QA consumes project contracts; it does not replace their requirements, criteria, states,
approvals, or governance authority.

## Status vocabulary

Case and criterion results are exactly `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `NOT_APPLICABLE`.
Global verdicts are exactly `PASS`, `FAIL`, or `BLOCKED`.

Evaluate a global verdict with this precedence:

1. A proven current in-scope failure is `FAIL`, including an in-scope defect with no associated
   criterion. `FAIL` prevails over pending work.
2. Without a proven current failure, any pending, insufficient, missing, or unsafe evidence is
   `BLOCKED`.
3. Missing criteria are `BLOCKED`. Zero applicable criteria are `BLOCKED`; never report a
   misleading success percentage for an empty denominator.
4. `PASS` requires all applicable criteria to pass and the absence of open or otherwise current
   in-scope defects.
5. Human risk acceptance does not change the recorded criterion or case result.

`NOT_RUN` records an applicable check that was not executed. `NOT_APPLICABLE` requires a stated
reason and does not erase the criterion. Neither value can be used to manufacture `PASS`.

## Workflow boundaries

| Workflow | Mode | Contract |
|---|---|---|
| `qa-init` | `observe` | Observe context and report available, missing, and unverified tools without installing them. |
| `qa-strategy` | `write` | Define risk, coverage, environments, data, and entry/exit criteria. |
| `qa-test` | `execute` | Execute authorized tests and bind results to evidence. |
| `qa-explore` | `execute` | Run an authorized charter and record observations and defects. |
| `qa-regression` | `write` | Select checks by impact and record the selection rationale. |
| `qa-bug` | `write` | Record reproduction, severity, priority, state, and retest. |
| `qa-review` | `read-only` | Review requirements, coverage, evidence, and findings without mutation. |
| `qa-release` | `write` | Produce a release verdict that exposes failures and pending work. |
| `qa-report` | `export` | Export a report from normalized data without executing evidence commands. |
| `qa-status` | `read-only` | Summarize existing QA state and its next valid action without mutation. |

`qa-review` and `qa-status` are read-only: they must not execute tests, mutate product or QA
artifacts, write approvals, or trigger external effects. A user must explicitly select and
authorize a mutating workflow before those actions occur.

## Common execution sequence

1. Identify the target, objective, contract, applicable criteria, and existing approvals.
2. Preserve criterion IDs and text. Do not infer a complete criterion catalog from arbitrary
   Markdown or from file hashes.
3. Confirm the workflow is installed and the requested operation is authorized.
4. Record tools as available, missing, or unverified from observed evidence.
5. Execute only the selected workflow. Missing capability becomes an explicit limitation.
6. Bind every result to its expected and observed values and to verified evidence when evidence
   is required.
7. Apply the verdict precedence above and expose all blockers and current defects.

## Output minimum

Every workflow output identifies the target and contract, criteria considered, operation,
results, limitations, evidence references, current defects, global verdict, and next valid
action. Metrics state their denominator; requirements coverage is not source-line coverage.
