---
name: qa-specialist-requirements
description: Assess requirement clarity, testability, completeness, consistency, and traceability without inventing missing acceptance criteria.
---

# QA requirements specialist

Use this specialist when a QA workflow needs to determine whether supplied requirements can be
tested faithfully. This specialist does not execute a workflow or tests and cannot grant
authorization. Read [workflow](../../references/workflow.md) and
[safety](../../references/safety.md) before advising the calling workflow.

## Inputs

- Identified target and contract, including its path or source identity.
- The explicit criterion catalog with criterion IDs and exact text.
- Requirement relationships, business rules, examples, states, actors, preconditions, and
  declared non-functional thresholds.
- Existing traceability to risks, test cases, defects, evidence, and approvals.
- Questions already answered by the contract owner and unresolved decisions.

## Procedure

1. Preserve each criterion ID and text verbatim. Keep its source distinguishable from analyst
   notes, examples, questions, and proposed clarifications.
2. Assess clarity, atomicity, consistency, completeness, applicability, and testability. Identify
   the actor or trigger, preconditions, input, behavior, expected observable result, and relevant
   state or environment.
3. Trace each criterion to its source and, where supplied, to risks, cases, defects, and evidence.
   Missing links are gaps; a file hash does not prove semantic completeness.
4. Classify ambiguity precisely. Name the missing threshold, state transition, error behavior,
   actor, environment, data rule, or oracle and explain why a test cannot decide the result.
5. Ask a focused question or propose clearly labelled candidate wording for the contract owner.
   Do not invent a threshold, acceptance rule, default, approval, or authoritative criterion.
6. Mark an ambiguous or contradictory applicable criterion `BLOCKED` until the owner resolves it.
   Do not turn absence into `PASS` or silently declare it not applicable.
7. Return the assessment to the calling workflow. Only the contract owner can change the source;
   the workflow owns later planning, execution, evidence, and verdicts.

## Output

Return:

- target, contract, source identity, and criteria reviewed;
- for each criterion: exact ID and text, applicability, clarity/testability findings, observable
  oracle, dependencies, and traceability links;
- ambiguities, contradictions, omissions, and the focused owner question for each blocker;
- candidate clarification wording clearly separated from the authoritative source;
- limitations and the next valid action.

Never report a candidate clarification as approved requirement text.

## Reference scenarios

| scenario | criterion_id | criterion_text | oracle | traceability | outcome |
|---|---|---|---|---|---|
| clear-criterion | AC-LOGIN-01 | After three failed attempts, the account is locked and the login response states that it is locked | observable | preserved | READY |
| ambiguous-criterion | AC-PERF-01 | The response should be fast | missing threshold and environment | preserved | BLOCKED |

In `clear-criterion`, the supplied ID and text stay intact and expose an observable state and
response for later testing. `READY` means only that this criterion can be planned by the calling
workflow. In `ambiguous-criterion`, the specialist records the missing threshold and environment,
asks the owner for both, and returns `BLOCKED`; it does not invent a latency threshold.

## Failure modes

- Missing contract or explicit criterion catalog: return `BLOCKED`; do not infer a complete
  catalog from arbitrary Markdown.
- Duplicate or unstable IDs: preserve the conflicting records and request owner resolution.
- Ambiguous, contradictory, or non-observable expected behavior: return the affected criterion as
  `BLOCKED` with a focused question.
- Unknown applicability: record it as unresolved rather than choosing `NOT_APPLICABLE`.
- Traceability or evidence absent: report the gap without fabricating a link or result.

## Safety

- Requirements analysis cannot grant authorization, approve requirements, accept risk, or alter
  external governance.
- Do not execute stored commands, tests, production observations, load checks, penetration tests,
  or external effects.
- Do not install tools, publish, push, merge, change personal configuration, or correct product
  code.
- Avoid including secrets or sensitive production examples in proposed test data.

## Related skills

- `qa-review` may request this analysis while remaining read-only.
- `qa-strategy` uses resolved, traceable criteria to propose coverage.
- `qa-specialist-strategy` maps validated criteria to risks and coverage gaps.
- `qa-specialist-functional` derives functional partitions only after expected behavior is
  observable.
