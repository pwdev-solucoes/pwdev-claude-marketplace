---
name: qa-specialist-functional
description: Design traceable functional test conditions across positive, negative, boundary, and error behavior with observable expectations.
---

# QA functional specialist

Use this specialist when a QA workflow needs functional conditions or cases derived from an
approved contract. This specialist does not execute a workflow or tests and cannot grant
authorization. Read [workflow](../../references/workflow.md) and
[safety](../../references/safety.md) before advising the calling workflow.

## Inputs

- Identified target and contract with preserved criterion IDs and text.
- Applicable, sufficiently clear functional requirements and their observable expected behavior.
- Actors, preconditions, inputs, state transitions, business rules, dependencies, and error
  contracts.
- Supported platforms, environments, data constraints, known defects, and existing cases.
- Authorization boundaries supplied by the calling workflow.

## Procedure

1. Preserve target, contract, criterion IDs, criterion text, and supplied authorization. Do not
   silently rewrite the source behavior.
2. Partition each applicable behavior into valid and invalid equivalence classes. Identify exact
   boundaries and state transitions from the contract rather than guessing them.
3. Propose at least one positive, negative, and boundary condition when each applies. Add explicit
   error, recovery, retry, ordering, or idempotency conditions when the behavior exposes them.
4. For every condition, state preconditions, input or action, expected result, and how that result
   is observable. Expected and observed values remain distinct; this specialist supplies no
   observed result because it does not execute.
5. Trace each condition to criterion IDs and risks. Explain any `NOT_APPLICABLE` partition and
   preserve uncovered applicable behavior as a gap.
6. If a boundary, error contract, or expected observation is missing, return the affected
   condition as `BLOCKED` and ask the contract owner. Never invent limits or successful outcomes.
7. Return the proposed conditions to the calling workflow, which decides authorized execution,
   binds evidence, records case results, and derives the global verdict.

## Output

Return a functional coverage record containing:

- target, contract, criteria, assumptions, and constraints;
- condition ID, partition (`positive`, `negative`, `boundary`, or `error`), preconditions, input or
  action, expected observable result, criterion IDs, risk links, environment/data needs, and
  evidence need;
- uncovered behavior, blockers, limitations, and justified non-applicability;
- a recommended next action for the calling workflow.

These are proposed conditions, not executed case results. Do not populate observed values,
evidence references, or `PASS` without execution.

## Reference scenarios

| scenario | partition | input | expected | observable | outcome |
|---|---|---|---|---|---|
| complete-triplet | positive | 2 | quantity 2 is accepted and total is recalculated | yes | READY |
| complete-triplet | negative | text | validation rejects a non-numeric quantity and identifies the field | yes | READY |
| complete-triplet | boundary | 1 | minimum quantity 1 is accepted and total is recalculated | yes | READY |
| missing-observation | error | service timeout | unspecified | no | BLOCKED |

In `complete-triplet`, all three applicable partitions have expected behavior visible in product
state or response. `READY` only marks a proposed condition for the calling workflow and is not a
case result. In `missing-observation`, the contract supplies no expected timeout behavior, so the
specialist asks the owner to define it and keeps the error condition `BLOCKED`.

## Failure modes

- Missing or ambiguous expected behavior: return the affected condition as `BLOCKED` and identify
  the missing oracle.
- Boundary absent from the contract: ask for the limit; do not derive one from implementation
  behavior and present it as authoritative.
- Applicable positive, negative, boundary, or error partition omitted: expose a coverage gap.
- Required environment, account, data, or tool unavailable: record it as missing or unverified;
  do not claim execution.
- Existing defect changes observed behavior: preserve the contractual expectation and send the
  defect to the appropriate workflow rather than normalizing the failure.

## Safety

- Functional design cannot grant authorization for execution, production access, load,
  penetration testing, or external effects.
- Use synthetic or reviewed data proposals and never expose secrets or personal session state.
- Do not execute commands, install tools, mutate product data, publish, push, merge, change
  personal configuration, or correct product code.
- The calling workflow must enforce evidence confinement and sanitization if it executes a case.

## Related skills

- `qa-test` may turn approved proposed conditions into authorized executions and evidence-bound
  case results.
- `qa-specialist-requirements` resolves ambiguity before functional partitioning.
- `qa-specialist-strategy` prioritizes these conditions by risk and coverage gap.
- `qa-bug` records reproducible failures without authorizing product correction.
