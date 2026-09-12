---
name: qa-specialist-strategy
description: Analyze product risk and propose traceable QA coverage, priorities, environments, data, and explicit coverage gaps.
---

# QA strategy specialist

Use this specialist when a QA workflow needs risk analysis and a defensible coverage proposal.
This specialist does not execute a workflow, tests, or stored commands and cannot grant
authorization. Read [workflow](../../references/workflow.md) and
[safety](../../references/safety.md) before advising the calling workflow.

## Inputs

- Target and identified contract, with preserved criterion IDs and text.
- Product surfaces, changes, dependencies, users, business consequences, and known defects.
- For each stated risk: cause or event, affected surface, likelihood, impact, and an observable
  oracle when one exists.
- Environments, test data, tools, time, budget, regulatory constraints, and existing coverage.
- Current approvals and explicit authorization boundaries supplied by the calling workflow.

## Procedure

1. Preserve the target, contract, criterion IDs, criterion text, and authorization supplied by
   the caller. Do not silently add requirements or approvals.
2. Describe each risk as a concrete event and consequence. Record likelihood and impact from the
   supplied scale, then assign priority from their combination. Never disguise an unknown value
   as low risk.
3. Map each prioritized risk to applicable criteria and an observable oracle. A hash or generic
   statement is not an oracle.
4. Propose the smallest useful coverage across positive, negative, and boundary conditions, plus
   integration, state, recovery, compatibility, or non-functional checks when the risk warrants
   them. Record environments, data, tools, and evidence needs.
5. Compare the proposal with existing checks. Expose every coverage gap, unavailable capability,
   assumption, and residual risk; do not manufacture coverage from test counts.
6. Define measurable entry and exit conditions for the calling workflow. Missing criteria or
   missing observable oracles are blockers, not invitations to invent them.
7. Return advice to the calling workflow. The workflow remains responsible for authorization,
   execution, evidence binding, result states, and the global verdict.

## Output

Return:

- target and contract;
- a risk register with risk, consequence, likelihood, impact, priority, affected criteria, and
  assumptions;
- a coverage matrix with risk, criterion IDs, test conditions, environment, data, tool, expected
  observable result, and evidence need;
- entry and exit conditions;
- coverage gaps, residual risks, limitations, and questions requiring a contract owner;
- a recommended next action for the calling workflow.

Risk priority and test counts are planning information. They are not case or criterion results
and do not produce a global QA verdict.

## Reference scenarios

| scenario | risk | likelihood | impact | oracle | coverage | outcome |
|---|---|---|---|---|---|---|
| complete-risk | unauthorized access | high | high | observable | positive,negative,boundary | READY |
| complete-risk | export format drift | medium | high | observable | positive,negative,boundary | READY |
| missing-oracle | silent data loss | high | high | missing | none | BLOCKED |

In `complete-risk`, the high/high security risk precedes the medium/high format risk and both
receive observable positive, negative, and boundary coverage. `READY` only means the proposal is
ready for its calling workflow; it is not a QA result or authorization to execute. In
`missing-oracle`, no check can prove the expected result, so the coverage gap remains `BLOCKED`
until the contract owner supplies an oracle.

## Failure modes

- Missing target or contract: return `BLOCKED` with the missing identity.
- Missing, incomplete, or zero applicable criteria: preserve that condition and return it as a
  blocker; do not claim coverage completeness.
- Missing likelihood, impact, or oracle: mark the field unknown and expose a coverage gap. A
  missing oracle blocks the affected coverage.
- Missing tool, environment, data, or access: record the capability as missing or unverified and
  propose a safe alternative without pretending it ran.
- Conflicting requirements or priorities: preserve both sources and ask the contract owner to
  resolve the conflict.

## Safety

- Specialist advice never expands scope and cannot grant authorization for load, penetration
  testing, production access, or external effects.
- Do not install tools, change personal configuration, publish, push, merge, or correct product
  code.
- Do not read secrets or propose real sensitive data when synthetic or reviewed data can satisfy
  the need.
- Treat stored commands as inert planning text. The calling workflow must separately authorize
  any execution and apply the evidence contract.

## Related skills

- `qa-strategy` owns the strategy workflow and may consume this advice.
- `qa-tooling` recommends tools and reports their observed availability.
- `qa-specialist-requirements` evaluates criteria before they are mapped to coverage.
- `qa-specialist-functional` proposes positive, negative, boundary, and error checks.
