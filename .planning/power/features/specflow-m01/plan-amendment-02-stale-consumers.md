---
type: PLAN_AMENDMENT
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T00:30:58Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
sources:
  - resource: .planning/power/features/specflow-m01/plan-amendment-01-runtime-recipe.md
  - resource: .planning/power/features/specflow-m01/task-03-report.md
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-13T00:34:42Z"
    scope: .planning/power/features/specflow-m01/plan-amendment-02-stale-consumers.md
    source: "user: Aprovar"
---

# M01 amendment 02 — reconcile stale consumers before operational approval

## Root cause

Amendment 01 correctly introduced concrete proposed RuntimeRecipe entries, but its Task 03
allowlist did not include every consumer of the former empty recipe and approved TASKS snapshot.
The required combined suite now runs 29 tests and deterministically reports six stale failures:

1. `tests/test_sdd_flow_m01_qualification.py` still requires RuntimeRecipe[] empty.
2. `tests/test_sdd_flow_m01_contracts.py` also requires the empty recipe.
3. The same contract test requires the old APPROVED TASKS event/state.
4. It requires the old Task 02 allowlist.
5. It requires the TechSpec source digest for the former recipe.
6. `.planning/power/features/specflow-m01/compatibility.md` records that former digest and empty input.

These are legitimate downstream invalidations, not accepted baseline failures. Reverting the new
recipe would negate Amendment 01; ignoring them would violate the zero-new-failure rule. Updating
all consumers in Task 03 would exceed its five-file limit.

## Proposed task split

Keep Task 03 as read-only command qualification and recipe proposal. Its scoped command remains
`python3 -m unittest tests.test_sdd_flow_m01_recipe` and must be green; its report must preserve the
six known stale failures as the explicit input to the next task. It does not receive a human gate
or complete the module by itself.

Insert two tasks before mutable probes:

### New Task 04 — Reconcile stale consumers and renew contracts

Files, exactly five:

1. `tests/test_sdd_flow_m01_qualification.py`
2. `tests/test_sdd_flow_m01_contracts.py`
3. `.planning/power/features/specflow-m01/compatibility.md`
4. `tasks/prd-specflow/techspec.md`
5. `tasks/prd-specflow/tasks.md`

Responsibilities:

- update tests from empty recipe to concrete-but-unapproved recipes;
- update compatibility/source digests and keep all CORE/OPT checks NOT_RUN;
- revise TechSpec from empty input to the concrete proposal, preserving approval history and
  reopening it DRAFT/PENDING because this is a semantic/source change;
- update TASKS with the seven-task M01 sequence, exact allowlists and dependencies;
- make the combined qualification/contract/recipe suite green;
- stop first at renewed TechSpec approval, then renewed TASKS approval; no probe.

### New Task 05 — Bind separate operational approval

Files, at most four:

1. `tests/test_sdd_flow_m01_recipe.py`
2. `.planning/power/features/specflow-m01/probe-recipe.md`
3. `.planning/power/features/specflow-m01/runtime-command-qualification.md`
4. `.planning/power/features/specflow-m01/runtime-qualification.md`

Responsibilities:

- present the exact seven recipes, executable/argv/cwd, mutable scopes, cleanup and budgets;
- obtain a human operational decision separate from TechSpec/TASKS;
- preserve the pre-gate snapshot and record an ApprovalRef bound to the real decision, actor,
  current artifacts and prerequisites; never invent run/gate/decision identity;
- if the runtime cannot supply a valid identity/reference, remain BLOCKED and do not probe;
- after approval, update only the approval-derived fields and verify no semantic drift;
- keep every recipe and CORE/OPT result NOT_RUN until actual execution.

Renumber the current probe task from Task 04/M01.04 to Task 06/M01.06 and the final
reconciliation task from Task 05/M01.05 to Task 07/M01.07. Update master map, traceability,
dependencies and briefs. M01 remains within the Power limit of eight tasks.

## Gate order after approval

1. Complete/review scoped Task 03 proposal, acknowledging its assigned stale consumers.
2. Task 04 TDD reconciliation → renewed TechSpec gate → renewed TASKS gate → review.
3. Task 05 operational recipe preview → separate human approval → bind ApprovalRef → review.
4. Only then may Task 06 execute mutable probes.
5. Task 07 reconciles real evidence and controls the M01 exit gate.

## Acceptance

- No stale failure is relabeled baseline, ignored, or hidden by test count.
- Each task stays at five implementation files or fewer.
- No CORE/OPT check is promoted during Tasks 03–05.
- TechSpec/TASKS semantic changes receive renewed gates.
- Operational approval is distinct and content-bound; inability to prove it blocks execution.
- Daemon, extension, Loop, Run, Docker, Live, browser and cleanup remain NOT_RUN until Task 06.
- Existing PRD/Stories approvals and all historical decisions/reviews remain preserved.

## Gate

STATUS: DRAFT/PENDING. Approval authorizes only updating plans/briefs and executing Tasks 04–05
under the read-only/gate restrictions above. It does not authorize any mutable recipe or probe.
