---
type: PLAN_AMENDMENT
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T00:07:36Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
sources:
  - resource: .planning/power/features/specflow-m01/plan.md
  - resource: .planning/power/features/specflow-m01/probe-recipe.md
  - resource: .planning/power/features/specflow-m01/task-02-gate-review.md
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-13T00:13:19Z"
    scope: .planning/power/features/specflow-m01/plan-amendment-01-runtime-recipe.md
    source: "user: sim"
---

# M01 amendment 01 — qualify a concrete runtime recipe before probes

## Problem

Task 02 is complete and reviewed, but Task 03 cannot satisfy its own precondition.
`probe-recipe.md` contains an empty `RuntimeRecipe[]`, `approved_scope: null`, no executable,
and no argv. Task 03 consumes that recipe and forbids execution when it is absent. No remaining
task owns the recipe file before Task 03, so dispatching the current Task 03 would be an
unauthorized probe or a predetermined BLOCKED result.

Read-only observations on 2026-09-13:

- executable discovered: `/Users/paulosoares/.local/bin/compozy`;
- version: `compozy 0.3.0-beta.16`;
- `extension validate [directory]` validates without running extension code;
- `loop validate --file <file>` validates without saving;
- `loop run --dry-run` previews without creating a run;
- `extension dev`, `loop create`, `loop run` without dry-run and `loop approve` are mutable;
- `compozy status --json` returned exit 69 because the daemon socket was unavailable;
- `compozy whoami --json` returned `{}`, so runtime identity is not yet demonstrated.

Help/version/status establish syntax and current availability only. They do not prove binding,
daemon behavior, human identity, gates, atomicity, history, confinement, or mutual exclusion.

## Proposed amendment

Insert a new **Task 03 — Qualify commands and approve RuntimeRecipe** before the existing probe
task. Renumber the current Task 03 to Task 04 and current Task 04 to Task 05; preserve their
existing file lists and acceptance criteria, changing only dependency/task references.

New Task 03 file limit:

1. `tests/test_sdd_flow_m01_recipe.py` — positive/negative structural tests for concrete argv,
   mutable scope, cleanup, stale approval, and absence of invented PASS.
2. `.planning/power/features/specflow-m01/runtime-command-qualification.md` — read-only command,
   version, help, status, expected/observed, exit code, and hashes.
3. `.planning/power/features/specflow-m01/probe-recipe.md` — concrete proposed RuntimeRecipe
   entries; executable/argv/cwd and mutable_scope are explicit, but results remain NOT_RUN and
   approved_scope remains null until its separate gate.
4. `.planning/power/features/specflow-m01/runtime-qualification.md` — link command qualification
   without converting any CORE/OPT check to PASS.
5. `tasks/prd-specflow/tasks.md` — add the new task contract and re-open the TASKS gate because
   its execution scope changes.

The report, review package, approval receipt, and ledger remain operational evidence outside the
five implementation files.

## Required sequence

1. Approve this amendment; this does not authorize mutable commands.
2. A fresh implementer uses TDD and only read-only `--help`, `version`, `status`, validation help,
   and filesystem-independent discovery to write the concrete proposal.
3. Present the changed TASKS contract for a renewed human gate.
4. Present the concrete recipe, exact mutable scope, cleanup policy, budgets, and command preview
   for a separate operational approval. Until then every recipe result is NOT_RUN and
   `approved_scope` is null.
5. Independently review the new Task 03. Only after both gates and a non-stale approval reference
   may the renumbered probe task execute its listed commands.

## Mutable scope that must be previewed later

No item below is authorized by approving this amendment. The future recipe must enumerate exact
values for: daemon start/health; one dedicated workspace/checkout identity; extension validation
and optional dev-link owned by the probe; Loop validation/publication/run IDs; Network Local;
synthetic fixture paths; bounded run/turn/time budgets; output/evidence paths; and cleanup limited
to recorded owned resources. It must exclude secrets, personal profiles, unrelated sessions,
global installation, Live, Docker, browser, merge, publication, and cleanup of unknown resources.

If daemon identity, workspace identity, human approval identity, cleanup ownership, or any argv
is unknown, the affected recipe remains BLOCKED/NOT_RUN. Starting the daemon or creating/linking
anything requires the later operational approval, not this planning gate.

## Acceptance

- The new task fits Power limits: five implementation files and no mutable execution.
- Existing Task 01/02 approvals and reviews remain historical; TASKS alone becomes stale because
  its scope changes.
- RuntimeRecipe entries contain no speculative executable/argv and no fabricated ApprovalRef.
- Read-only evidence distinguishes PASS for command discovery from NOT_RUN for behavior.
- The probe task remains blocked until concrete recipes, renewed TASKS, operational scope, cleanup,
  budgets, and human approval reference are all current.
- No CORE/OPT guarantee becomes PASS during command qualification.

## Gate

STATUS: DRAFT/PENDING. Approval authorizes only updating the M01 plan/briefs and executing the new
read-only qualification task. It does not authorize daemon start, extension linking, Loop
creation/run/approval, Docker, Live, browser, installation, cleanup, or any other mutable probe.
