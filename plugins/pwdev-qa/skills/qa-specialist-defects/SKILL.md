---
name: qa-specialist-defects
description: Triage defects with independent severity and priority, reproducible evidence, preserved attempt history, and explicit resolution retesting.
---

# QA defects specialist

Use this specialist when a QA workflow needs to record, triage, or reassess a defect for an
identified target and contract. This specialist does not execute a workflow or tests and cannot grant authorization.
Read [workflow](../../references/workflow.md),
[safety](../../references/safety.md), [artifacts](../../references/artifacts.md), and
[tooling](../../references/tooling.md) before advising the calling workflow.

## Inputs

- Target, environment, build/change identity, identified contract, preserved criterion IDs/text,
  and applicable authorization.
- Summary, prerequisites, deterministic reproduction steps, inputs, expected and observed values,
  frequency, affected surface, scope, and valid target-bound evidence.
- Severity assessment based on product/user impact and priority assessment based on delivery
  order, urgency, dependencies, and business scheduling, each with its own rationale and owner.
- Defect state, stable defect ID, linked or intentionally empty criterion IDs, original failure
  attempt, all later attempts, supersession links, and proposed or completed retest evidence.

## Procedure

1. Preserve target, contract, criteria, approvals, defect identity, and existing state. An empty
   criterion link does not make a proven in-scope defect disappear; record why it is unlinked.
2. Establish reproduction with prerequisites, exact steps, expected and observed behavior,
   affected build/environment, frequency, scope, and evidence. If reproduction or evidence is
   insufficient, keep the finding explicit and `BLOCKED`; do not fabricate certainty.
3. Assess severity from product impact and user impact independently from priority. Assess priority
   from delivery order and operational urgency. Record both rationales; neither value derives
   automatically from the other, and human risk acceptance does not rewrite the failure result.
4. Preserve immutable history for the original failure and every retest attempt. Use stable
   logical case identity, increasing attempt numbers, and valid supersession links; never delete a
   failed attempt or rerun until pass.
5. Mark a defect `resolved` only when its referenced terminal retest attempt is `PASS` and its
   evidence is valid, current, confined, target-bound, and sanitized. A blocked or failed terminal
   retest keeps the defect current; never fall back to an older passing attempt.
6. Apply verdict precedence. Any proven current in-scope failure is `FAIL`, including an open or
   otherwise current defect whose criterion IDs are empty. Without proof of current failure,
   missing reproduction, evidence, or retest is `BLOCKED`. `PASS` requires all applicable
   criteria to pass and no current in-scope defects.
7. Return the defect record, triage, history, retest state, evidence references, verdict input,
   and next authorized action without changing product code.

## Output

Return:

- target, contract, criteria or explicit unlinked reason, environment, build, and authorization;
- defect ID, summary, scope, prerequisites, reproduction, expected/observed behavior, frequency,
  severity and rationale, priority and rationale, owner, state, and related risks;
- complete attempt history with stable case ID, unique attempt IDs, supersession, status,
  expected/observed values, retest linkage, and verified evidence references;
- current-defect decision, blockers, limitations, global verdict input, and next valid action.

## Reference scenarios

| scenario | severity | priority | status | history | retest | evidence | defect_current | applicable_criteria | other_current_defects | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| verified-resolution | critical product impact | P1 delivery order | resolved | original failure and all attempts preserved | terminal PASS attempt | valid original and retest evidence | false | not evaluated by defect resolution | not evaluated | BLOCKED |
| all-applicable-pass | critical product impact | P1 delivery order | resolved | original failure and all attempts preserved | terminal PASS attempt | valid original and retest evidence | false | explicit complete catalog AC-LOGIN-01=PASS AC-SESSION-02=PASS | none | PASS |
| missing-criteria-catalog | critical product impact | P1 delivery order | resolved | original failure and all attempts preserved | terminal PASS attempt | valid original and retest evidence | false | missing | none | BLOCKED |
| missing-defect-inventory | critical product impact | P1 delivery order | resolved | original failure and all attempts preserved | terminal PASS attempt | valid original and retest evidence | false | explicit complete catalog AC-LOGIN-01=PASS AC-SESSION-02=PASS | not evaluated | BLOCKED |
| other-current-defect | critical product impact | P1 delivery order | resolved | original failure and all attempts preserved | terminal PASS attempt | valid original and retest evidence | false | explicit complete catalog AC-LOGIN-01=PASS AC-SESSION-02=PASS | DEF-OTHER-02 proven current | FAIL |
| proven-unlinked-current | major product impact | P2 delivery order | open | original failure preserved | NOT_RUN | valid in-scope failure evidence | true | no criterion associated | none | FAIL |

Resolution produces the verdict input `defect_current=false`; it does not produce global `PASS`.
Only `all-applicable-pass` has an explicit complete catalog with every applicable criterion
`PASS` and an explicit empty current-defect inventory. Missing either inventory is `BLOCKED`;
another proven current defect is `FAIL`. The unlinked current failure also forces `FAIL`.

## Failure modes

- Missing reproduction, expected/observed behavior, target, scope, or valid evidence: preserve the
  finding and return the unresolved assessment as `BLOCKED` unless other valid evidence proves a
  current in-scope failure.
- Severity copied into priority, or priority used to reduce severity/status: separate the two
  decisions and request distinct rationales; do not change the recorded result.
- `resolved` without a referenced terminal `PASS` retest and valid evidence: keep the defect
  current. Valid original failure evidence implies `FAIL`; otherwise evidence insufficiency is
  `BLOCKED`.
- Retest branch, cycle, missing attempt, different case/target, or fallback to an older pass:
  reject that resolution conclusion and preserve the complete history.
- Missing criterion association: state it explicitly, preserve traceability debt, and still return
  `FAIL` when the current in-scope defect is proven.
- Unsafe, changed, missing, or target-incompatible evidence: do not attach it and prevent `PASS`.

## Safety

- This specialist cannot grant execution, production, external-effect, load, penetration-test,
  deployment, publication, or merge authorization.
- Finding or triaging a defect is not permission to correct product code. Never execute stored
  commands, install tools, alter personal configuration, publish, push, merge, or deploy.
- Keep evidence local, regular, confined, target-bound, immutable during assessment, and reviewed
  for sanitization before attachment.

## Related skills

- `qa-bug` records and updates defect lifecycle information from this specialist.
- `qa-test` may perform a separately authorized retest and bind valid evidence.
- `qa-specialist-regression` uses defect and retest history to prioritize coverage.
- `qa-specialist-production` can connect an authorized incident observation to a defect and a
  preventive regression proposal.
