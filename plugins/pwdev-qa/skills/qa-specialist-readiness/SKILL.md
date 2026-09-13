---
name: qa-specialist-readiness
description: Assess release readiness from applicable criteria, all current defects, risks, limitations, and recorded human decisions without approving release.
---

# QA readiness specialist

Use this specialist when a QA workflow needs a release recommendation for an identified target,
contract, and build. This specialist does not execute a workflow, tests, release, deployment, or
stored commands and cannot grant authorization. Read [workflow](../../references/workflow.md),
[safety](../../references/safety.md), and [artifacts](../../references/artifacts.md) before
advising the calling workflow.

## Inputs

- Target, build/change identity, contract, complete criterion catalog with applicability and
  results, and verified evidence references.
- Complete current defect inventory, including proven in-scope defects with no associated
  criterion, plus retest and resolution evidence.
- Known risks, owners, mitigations, residual exposure, limitations, missing capabilities,
  pending work, and unsafe or insufficient evidence.
- Existing human release decision and risk decisions, with decision maker, authority, scope,
  rationale, and timestamp; absence is recorded, never inferred.

## Procedure

1. Preserve target, build, contract, criterion IDs/text, results, approvals, and human decisions.
   This specialist recommends; it does not approve release or manufacture authority.
2. Confirm the criterion catalog is complete. Evaluate every applicable criterion and preserve
   every `NOT_APPLICABLE` item with its reason. Zero applicable criteria is `BLOCKED`.
3. Inventory all current in-scope defects independently of criterion links. A proven current
   failure is `FAIL`, including a defect with no criterion association, and takes precedence over
   pending work or human risk acceptance.
4. Evaluate known risks, mitigations, residual risks, evidence safety/sufficiency, unavailable
   capabilities, and all limitations. Without a proven current failure, any pending, missing,
   insufficient, unsafe, or unresolved item is `BLOCKED`.
5. Record the human release decision and any risk decision separately from QA results. Risk
   acceptance does not rewrite `FAIL`, `BLOCKED`, or an underlying case/criterion result. A missing
   required human decision is pending and therefore `BLOCKED`.
6. Apply verdict precedence: proven current in-scope failure means `FAIL`; otherwise pending work,
   zero applicable criteria, or missing information means `BLOCKED`; `PASS` requires all
   applicable criteria `PASS`, no current in-scope defects, no pending risk or limitation, and the
   required human decision recorded.
7. Recommend release only for `PASS`, recommend against release for `FAIL`, or name the exact
   decision/blocker for `BLOCKED`. Return that recommendation to the release owner without
   deploying, publishing, changing approvals, or autoapproving release.

## Output

Return:

- target, build, contract, complete applicable/non-applicable criterion inventory, results, and
  evidence references;
- complete current defect inventory including unlinked defects, retest state, and evidence;
- risks, mitigations, residual risks, limitations, missing/unsafe evidence, and pending work;
- human release/risk decision with actor, authority, scope, rationale, and timestamp, or an
  explicit missing-decision blocker;
- global verdict `PASS`, `FAIL`, or `BLOCKED`, its traceable rationale, release recommendation,
  recommendation owner, and next valid action.

## Reference scenarios

| scenario | applicable_criteria | current_defects | risks | limitations | decision_record | decision_actor | decision_authority | decision_scope | decision_rationale | decision_timestamp | verdict | recommendation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| release-ready | AC-LOGIN-01=PASS AC-SESSION-02=PASS | none including unlinked inventory | none unresolved | none pending | recorded approve | release-owner-17 | production release owner | checkout-api build rc-17 | all applicable criteria passed and no current defects or pending risks | 2026-09-12T18:30:00Z | PASS | recommend release without approving it |
| proven-unlinked-failure | AC-LOGIN-01=PASS AC-SESSION-02=PASS | DEF-UNLINKED-01 proven current in scope | accepted operational risk | none pending | recorded risk acceptance | release-owner-17 | production release owner | checkout-api build rc-17 | accept operational risk for scheduled window | 2026-09-12T18:30:00Z | FAIL | do not release |
| pending-limitation | AC-LOGIN-01=PASS AC-SESSION-02=PASS | none including unlinked inventory | none unresolved | browser evidence pending | missing | missing | missing | missing | missing | missing | BLOCKED | resolve pending evidence and decision |
| zero-applicable | zero applicable criteria | none including unlinked inventory | none unresolved | no executable release criteria | recorded approve | release-owner-17 | production release owner | checkout-api build rc-18 | owner requests release after catalog review | 2026-09-12T19:30:00Z | BLOCKED | define applicable criteria |
| missing-decision-record | AC-LOGIN-01=PASS AC-SESSION-02=PASS | none including unlinked inventory | none unresolved | none pending | missing | release-owner-17 | production release owner | checkout-api build rc-17 | all applicable criteria passed and no current defects or pending risks | 2026-09-12T18:30:00Z | BLOCKED | obtain complete human decision |
| missing-decision-actor | AC-LOGIN-01=PASS AC-SESSION-02=PASS | none including unlinked inventory | none unresolved | none pending | recorded approve | missing | production release owner | checkout-api build rc-17 | all applicable criteria passed and no current defects or pending risks | 2026-09-12T18:30:00Z | BLOCKED | obtain complete human decision |
| missing-decision-authority | AC-LOGIN-01=PASS AC-SESSION-02=PASS | none including unlinked inventory | none unresolved | none pending | recorded approve | release-owner-17 | missing | checkout-api build rc-17 | all applicable criteria passed and no current defects or pending risks | 2026-09-12T18:30:00Z | BLOCKED | obtain complete human decision |
| missing-decision-scope | AC-LOGIN-01=PASS AC-SESSION-02=PASS | none including unlinked inventory | none unresolved | none pending | recorded approve | release-owner-17 | production release owner | missing | all applicable criteria passed and no current defects or pending risks | 2026-09-12T18:30:00Z | BLOCKED | obtain complete human decision |
| missing-decision-rationale | AC-LOGIN-01=PASS AC-SESSION-02=PASS | none including unlinked inventory | none unresolved | none pending | recorded approve | release-owner-17 | production release owner | checkout-api build rc-17 | missing | 2026-09-12T18:30:00Z | BLOCKED | obtain complete human decision |
| missing-decision-timestamp | AC-LOGIN-01=PASS AC-SESSION-02=PASS | none including unlinked inventory | none unresolved | none pending | recorded approve | release-owner-17 | production release owner | checkout-api build rc-17 | all applicable criteria passed and no current defects or pending risks | missing | BLOCKED | obtain complete human decision |

`release-ready` produces a QA recommendation after a separately supplied human decision; the
specialist does not approve or execute the release. In `proven-unlinked-failure`, human risk
acceptance cannot erase the proven current failure. Pending evidence or a zero-applicable catalog
remains `BLOCKED`.
The `missing-decision-*` rows keep the QA assessment separate from the supplied human record and
show that omitting any one decision component is `BLOCKED`, never implicit approval.

## Failure modes

- Missing, partial, or zero-applicable criterion catalog: return `BLOCKED`; do not infer `PASS`.
- Missing current-defect inventory, including review for unlinked defects: return `BLOCKED` unless
  available evidence already proves a current in-scope failure, which returns `FAIL`.
- Proven current in-scope failure: return `FAIL` regardless of pending work, criterion linkage,
  severity, priority, waiver, or human risk acceptance.
- Pending risk, limitation, decision, retest, capability, or evidence: without a proven failure,
  return `BLOCKED` and name its owner and next valid action.
- Human decision without actor, authority, scope, rationale, or timestamp: preserve it as
  incomplete and `BLOCKED`; do not repair or approve it.

## Safety

- This specialist cannot grant release, deployment, execution, production, load,
  penetration-test, external-effect, publication, push, or merge authorization.
- A recommendation does not approve release and does not modify a recorded human decision.
- Do not execute commands, install tools, alter personal configuration, deploy, publish, merge,
  or correct product code.
- Cite only local, regular, confined, target-bound, integrity-checked, and sanitized evidence.

## Related skills

- `qa-release` owns the release workflow and may consume this recommendation.
- `qa-specialist-metrics` supplies scoped measurements but cannot replace readiness inputs.
- `qa-specialist-defects` determines whether defects remain current after retesting.
- `qa-status` summarizes the recorded verdict and next action without mutation.
