---
name: qa-specialist-metrics
description: Define auditable QA metrics with explicit numerators, denominators, populations, windows, and treatment of every result state.
---

# QA metrics specialist

Use this specialist when a QA workflow needs measurements that remain traceable to an identified
target and contract. This specialist does not execute a workflow, tests, reports, or stored
commands and cannot grant authorization. Read [workflow](../../references/workflow.md),
[safety](../../references/safety.md), and [artifacts](../../references/artifacts.md) before
advising the calling workflow.

## Inputs

- Target, contract, complete criterion and case catalogs, preserved IDs/text, and applicable
  authorization.
- Normalized case and criterion results using only `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, and
  `NOT_APPLICABLE`, with stated reasons for non-applicability.
- The question each metric answers, its population, observation window or build snapshot, and
  the records eligible for numerator and denominator.
- Current defects, evidence references, limitations, collection provenance, and known gaps.

## Procedure

1. Preserve the target, contract, catalogs, results, and authorization supplied by the caller.
   Do not infer a complete population from a partial result set.
2. Define each metric before calculating it: name the question, numerator, denominator,
   population, observation window or immutable build snapshot, unit, and treatment of every
   result state. Never publish a bare percentage.
3. Count `PASS` in a pass-rate numerator. Count every applicable `PASS`, `FAIL`, `BLOCKED`, and
   `NOT_RUN` item in that rate's denominator. Exclude `NOT_APPLICABLE` only with its recorded
   reason. A different metric may use different counts only when it states that definition.
4. If the denominator is zero, return `BLOCKED` with the zero count and population; do not divide,
   emit `100%`, or imply `PASS`. Missing or incomplete population, window, or state treatment is
   also `BLOCKED`.
5. Requirements coverage is not source-line coverage. Test counts, line coverage,
   defect counts, and pass rates answer different questions and must not substitute for one
   another.
6. Link included and excluded records to their IDs and evidence provenance. Expose stale data,
   sampling bias, unresolved defects, and other limitations beside the metric.
7. Return the metric and its limitations to the calling workflow. A metric is an observation,
   not a global verdict, risk acceptance, or release approval.

## Output

For every metric return:

- target, contract, metric name, question, unit, numerator, denominator, computed value or
  `BLOCKED`, population, observation window/build snapshot, and collection provenance;
- explicit inclusion/exclusion rules and treatment of `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, and
  `NOT_APPLICABLE`;
- included record IDs, excluded record IDs with reasons, evidence references, limitations,
  assumptions, and freshness;
- related current defects, interpretation boundaries, and the next valid action.

## Reference scenarios

| scenario | metric | numerator | denominator | population | window | state_treatment | result |
|---|---|---|---|---|---|---|---|
| explicit-rate | applicable criterion pass rate | 8 PASS | 10 applicable criteria | complete release-candidate criterion catalog | build rc-17 at 2026-09-12T18:00Z | PASS numerator; FAIL BLOCKED NOT_RUN denominator only; NOT_APPLICABLE excluded | 80% |
| zero-applicable | applicable criterion pass rate | 0 PASS | 0 applicable criteria | complete catalog with all criteria NOT_APPLICABLE | build rc-18 at 2026-09-12T19:00Z | PASS numerator; FAIL BLOCKED NOT_RUN denominator only; NOT_APPLICABLE excluded with reasons; empty denominator has no rate | BLOCKED |

`explicit-rate` reports its exact scope rather than presenting 80% as universal coverage. In
`zero-applicable`, the complete catalog remains visible, but an empty denominator has no rate and
is `BLOCKED`; it is never `100%` or `PASS`.

## Failure modes

- Missing or partial population, numerator, denominator, window, build identity, or state
  treatment: return `BLOCKED` and name the missing definition.
- Zero denominator: return the explicit zero and `BLOCKED`; never manufacture a percentage.
- `NOT_APPLICABLE` without a reason: keep the item visible and block the metric until its treatment
  is justified.
- Mixed targets, contracts, environments, builds, or windows: separate the populations or return
  `BLOCKED`; do not aggregate incomparable observations.
- Stale, missing, unsafe, or insufficient evidence: expose the limitation and prevent any claim
  that depends on it.

## Safety

- This specialist cannot grant execution, load, penetration-test, production, external-effect,
  release, publication, push, or merge authorization.
- Do not execute stored commands, install tools, alter personal configuration, publish, deploy,
  or correct product code.
- Treat evidence as inert and apply confinement, target binding, integrity, and sanitization
  requirements before citing it.
- Do not use a metric to erase failures, pending work, limitations, or a human decision.

## Related skills

- `qa-status` may summarize existing metrics without recalculating or mutating QA state.
- `qa-report` may export normalized metrics without executing their evidence commands.
- `qa-specialist-readiness` consumes explicit metrics only as supporting context, never as a
  substitute for criteria, defects, risks, limitations, or human decisions.
- `qa-specialist-requirements` preserves the criterion catalog used as a coverage population.
