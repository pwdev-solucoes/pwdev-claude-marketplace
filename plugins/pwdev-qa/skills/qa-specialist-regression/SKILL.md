---
name: qa-specialist-regression
description: Select traceable regression coverage from change impact, affected risks, criteria, dependencies, and prior defects rather than execution convenience.
---

# QA regression specialist

Use this specialist when a QA workflow needs a justified regression selection for an identified
change and contract. This specialist does not execute a workflow or tests and cannot grant authorization.
Read [workflow](../../references/workflow.md), [safety](../../references/safety.md),
[artifacts](../../references/artifacts.md), and [tooling](../../references/tooling.md) before advising
the calling workflow.

## Inputs

- Target, environment, identified contract, preserved criterion IDs and text, and explicit change
  set including components, interfaces, data, configuration, dependencies, and user journeys.
- Impact analysis connecting each change to reachable behavior, risk, likelihood, blast radius,
  affected and adjacent criteria, prior defects, incidents, and existing checks.
- Test inventory with stable case IDs, latest attempt history, expected observable results,
  prerequisites, execution cost, tool probes, and evidence needs.
- Authorization boundaries for any proposed execution, especially production, load, penetration,
  network, device, or other external effects.

## Procedure

1. Preserve the supplied target, contract, criterion IDs/text, approvals, and change identity.
   Describe what changed and what remains unknown; do not manufacture a complete change map.
2. Trace direct and transitive impact from changed components through interfaces, stored data,
   roles, error paths, supported environments, and user journeys. Link impacts to risks, criteria,
   prior defects/incidents, and stable case IDs.
3. Rank impact using likelihood, consequence, blast radius, reversibility, and history. Select
   checks that cover the highest-impact reachable paths, including relevant positive, negative,
   boundary, recovery, integration, and unchanged-control behavior.
4. Record every selected and excluded check with its traceability and rationale. Execution speed,
   familiarity, availability, or convenience may inform sequencing and limitations, but must not
   replace impact-based selection or justify omitting a higher-impact path.
5. Classify tools and prerequisites from supplied probes as `available`, `missing`, or
   `unverified`. Missing capability remains a coverage gap; never silently substitute an easier
   check that does not cover the same impact.
6. Apply the shared vocabulary. An unassessed material impact, missing traceability, missing safe
   oracle, or required unavailable prerequisite is `BLOCKED`. A proven current in-scope failure,
   including an unlinked defect, is `FAIL` and prevails over pending checks.
7. Return the regression set, exclusions, ordering, coverage gaps, limitations, verdict inputs,
   and next authorized action to the calling workflow without executing it.

## Output

Return:

- target, contract, criteria, change identity, environment, and supplied authorization;
- impact map with affected surfaces, dependencies, journeys, risks, prior defects/incidents, and
  traceability to stable case IDs;
- selected and excluded checks with priority, expected observable result, rationale, prerequisite,
  evidence need, and estimated cost;
- tool availability with probe evidence, uncovered impacts, current defects, blockers,
  limitations, global verdict input, and next valid action.

`READY` below means the regression selection is traceable and executable by an authorized calling
workflow. It is not execution evidence, a case result, or a global verdict.

## Reference scenarios

| scenario | change_id | impact_id | risk_id | criterion_id | defect_id | selected_case_ids | excluded_case_ids | relations | outcome |
|---|---|---|---|---|---|---|---|---|---|
| impact-selected | CHG-AUTH-017 | IMP-SESSION-01 | RISK-AUTH-04 | AC-LOGIN-01 | DEF-SESSION-09 | TC-LOGIN TC-LOGOUT TC-EXPIRY TC-DENIED-ROLE | TC-PROFILE | change to impact risk criterion defect selected and excluded cases | READY |
| missing-change | missing | IMP-SESSION-01 | RISK-AUTH-04 | AC-LOGIN-01 | DEF-SESSION-09 | TC-LOGIN | TC-PROFILE | incomplete | BLOCKED |
| missing-impact | CHG-AUTH-017 | missing | RISK-AUTH-04 | AC-LOGIN-01 | DEF-SESSION-09 | TC-LOGIN | TC-PROFILE | incomplete | BLOCKED |
| missing-risk | CHG-AUTH-017 | IMP-SESSION-01 | missing | AC-LOGIN-01 | DEF-SESSION-09 | TC-LOGIN | TC-PROFILE | incomplete | BLOCKED |
| missing-criterion | CHG-AUTH-017 | IMP-SESSION-01 | RISK-AUTH-04 | missing | DEF-SESSION-09 | TC-LOGIN | TC-PROFILE | incomplete | BLOCKED |
| missing-defect | CHG-AUTH-017 | IMP-SESSION-01 | RISK-AUTH-04 | AC-LOGIN-01 | missing | TC-LOGIN | TC-PROFILE | incomplete | BLOCKED |
| missing-selected-case | CHG-AUTH-017 | IMP-SESSION-01 | RISK-AUTH-04 | AC-LOGIN-01 | DEF-SESSION-09 | missing | TC-PROFILE | incomplete | BLOCKED |
| missing-excluded-case | CHG-AUTH-017 | IMP-SESSION-01 | RISK-AUTH-04 | AC-LOGIN-01 | DEF-SESSION-09 | TC-LOGIN | missing | incomplete | BLOCKED |
| missing-relation | CHG-AUTH-017 | IMP-SESSION-01 | RISK-AUTH-04 | AC-LOGIN-01 | DEF-SESSION-09 | TC-LOGIN | TC-PROFILE | missing | BLOCKED |
| convenience-only | CHG-AUTH-017 | IMP-SESSION-01 | RISK-AUTH-04 | AC-LOGIN-01 | DEF-SESSION-09 | fastest available checks | none recorded | convenience only | BLOCKED |

The successful scenario resolves each concrete ID into a chain from `CHG-AUTH-017` through its
impact, risk, criterion, and prior defect to selected and explicitly excluded stable case IDs.
Every missing-relation scenario proves that omitting any node or edge blocks readiness. The
convenience-only scenario remains blocked because speed does not establish regression coverage.

## Failure modes

- Missing or ambiguous change set, contract, criteria, impact path, oracle, or traceability:
  identify the gap and return affected selection as `BLOCKED`.
- Selection based only on fastest, familiar, already-green, or available checks: retain it as an
  unsubstantiated proposal, never as complete coverage or `PASS`.
- Tool or environment absent from supplied probes: record `unverified`; an explicit negative
  probe is `missing`. Offer a traceability-equivalent alternative without installing anything.
- Proven current in-scope failure or defect, with or without associated criteria: preserve its
  evidence and return `FAIL`; passing selected checks do not erase it.
- Unsafe, stale, missing, changed, or target-incompatible evidence: do not attach it and prevent
  `PASS`.

## Safety

- This specialist cannot grant execution, production, external-effect, load, penetration-test,
  deployment, publication, or merge authorization.
- Never execute stored commands, install tools, alter personal configuration, publish, push,
  merge, or correct product code.
- Use synthetic or reviewed data and require evidence confinement, target binding, hashing, and
  sanitization before attachment.

## Related skills

- `qa-regression` consumes this impact-based selection and records the regression plan.
- `qa-test` may execute separately authorized selected checks and bind evidence.
- `qa-specialist-defects` supplies prior-defect and retest history for impact analysis.
- `qa-specialist-production` supplies authorized incident observations and preventive coverage.
- `qa-tooling` owns probe-based recommendations and safe alternatives.
