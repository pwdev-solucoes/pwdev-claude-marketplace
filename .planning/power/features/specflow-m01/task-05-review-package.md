# Task 05 — snapshot review package

- Plan: `.planning/power/features/specflow-m01/plan.md`
- Amendments: `.planning/power/features/specflow-m01/plan-amendment-03-pre-run-approval.md`, `.planning/power/features/specflow-m01/plan-amendment-04-addressable-snapshot.md`
- Brief: `.planning/power/features/specflow-m01/task-05-brief.md`
- Report: `.planning/power/features/specflow-m01/task-05-report.md`
- Base/HEAD: `fb146297d681a1a6a77d71b5c30772655802590a`
- Packaging: integral snapshot; no task commit is authorized.

Read every file in full and verify hashes. Recompute `run_id` and `decision_id` from the canonical UTF-8/LF records. Verify the pre-approval snapshot ArtifactRef, prerequisite order, all seven recipes, NOT_RUN preservation, and separation from future Loop IDs.

| File | SHA-256 |
|---|---|
| `tests/test_sdd_flow_m01_recipe.py` | `0dab58d2f22f810da9a9a14193218f7f324f4302296baf12eef4928581173e83` |
| `.planning/power/features/specflow-m01/probe-recipe.md` | `0676fb34950a4ea68d6a4c4c9008da3a192354941e62ddb31611aa1218e8a82d` |
| `.planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md` | `c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4` |
| `.planning/power/features/specflow-m01/runtime-command-qualification.md` | `1d9b2152a2350ecf23d084ccb80a24449c0df6d3d75f9d8401ffe7cfba196a6f` |
| `.planning/power/features/specflow-m01/runtime-qualification.md` | `b68d20dd9e460b18a21d193f1bd571afd991b538888d574d0599da4001cf446a` |
| `.planning/power/features/specflow-m01/task-05-brief.md` | `14da2689b344e1bb23b86782647f781b4705461131d4033519c2775987410d8e` |
| `.planning/power/features/specflow-m01/task-05-report.md` | `69df49381ccd5d09951ac7069b92a2faf8d1d005a5dde250c46d9b1dd524e7b7` |
| `.planning/power/features/specflow-m01/plan-amendment-03-pre-run-approval.md` | `a7095c6ce1004d1e30d920c0efc272e1ec5797adffa02bf4fd236d88f7e4da25` |
| `.planning/power/features/specflow-m01/plan-amendment-04-addressable-snapshot.md` | `24a2f3ca06f712cdb464da5f680df1b8a83f99e53dfade88058dcff6b3b1dcf0` |

Fresh controller verification: combined M01 suite ran 33 tests, exit 0; `git diff --check` exit 0. No probe command was executed.
