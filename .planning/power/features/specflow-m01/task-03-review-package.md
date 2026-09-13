# Task 03 — snapshot review package

- Plan: `.planning/power/features/specflow-m01/plan.md`
- Brief: `.planning/power/features/specflow-m01/task-03-brief.md`
- Report: `.planning/power/features/specflow-m01/task-03-report.md`
- Base/HEAD: `fb146297d681a1a6a77d71b5c30772655802590a`
- Packaging: integral snapshot, because the approved task forbids commits and the task files are untracked relative to BASE.

The reviewer must read every file below in full and verify the recorded SHA-256 before judging. The six combined-suite failures are not accepted baseline or success: Amendment 02 assigns their exact reconciliation to Task 04, while Task 03 must preserve their IDs/causes and keep its focused suite green.

| File | SHA-256 |
|---|---|
| `tests/test_sdd_flow_m01_recipe.py` | `95a8d764287383dd819ccd3a369819ccd43de4cda98955c426345f410c4ff368` |
| `.planning/power/features/specflow-m01/runtime-command-qualification.md` | `1d9b2152a2350ecf23d084ccb80a24449c0df6d3d75f9d8401ffe7cfba196a6f` |
| `.planning/power/features/specflow-m01/probe-recipe.md` | `c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4` |
| `.planning/power/features/specflow-m01/runtime-qualification.md` | `b68d20dd9e460b18a21d193f1bd571afd991b538888d574d0599da4001cf446a` |
| `tasks/prd-specflow/tasks.md` | `f308a46ba088f7daa54c04657a43a430b6269982445ad22c83418459b0cc1da6` |
| `.planning/power/features/specflow-m01/task-03-brief.md` | `e1226113763a45174bd39619d74a620c63f5ea9df6263baeef07843e8092950d` |
| `.planning/power/features/specflow-m01/task-03-report.md` | `02fbe1f25e98f8722f5daf3cce44985d206eae0e9c5cdd2eaf626f5e6e23699f` |

Fresh controller verification:

- `python3 -m unittest tests.test_sdd_flow_m01_recipe`: 6 tests, exit 0, OK.
- `python3 -m unittest tests.test_sdd_flow_m01_recipe tests.test_sdd_flow_m01_qualification tests.test_sdd_flow_m01_contracts`: 30 tests, exit 1, exactly six failures matching the report and Amendment 02 handoff.
- No mutable runtime command or probe was executed by the controller.
