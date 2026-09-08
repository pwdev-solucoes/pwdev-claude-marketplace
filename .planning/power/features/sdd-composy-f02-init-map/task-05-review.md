# Task 05 review — Codebase map helper

## Verdict

- SPEC: FAIL
- QUALITY: FAIL
- Findings: 1 blocker

## Findings

### [BLOCKER] Task 05 implementation and required contract artifacts are absent

The approved F02 plan and `task-05-brief.md` require all of the following deliverables:

- `plugins/sdd-composy/scripts/sdd_map.py`
- `plugins/sdd-composy/references/mapping.md`
- fixture coverage in `tests/test_sdd_composy_runtime.py` for stack detection, manifest-derived commands, domain evidence, staleness, and secret exclusion
- `task-05-report.md`

None of these files is present in the reviewed worktree at commit `acf1970`. Consequently there is no read-only repository-bound inventory, no secret/environment exclusion implementation, no adaptive stack or manifest command detection, no domain-evidence extraction, no source-commit/staleness calculation, no deterministic `codebase.json` serializer, and no OKF context-concept publication to review. The F01/F02 contracts do define the required destinations and invariants: operational context belongs under `.planning/sdd-composy/context/`, `context/codebase.json` is the map artifact, writes must be atomic, unknown JSON fields must be preserved by supported updates, and the map is observational rather than architectural intent. The missing helper cannot currently satisfy or demonstrate any of those requirements.

The focused runtime suite currently passes only the pre-existing foundation coverage (`python3 -m unittest tests.test_sdd_composy_runtime`: 16 tests passed); it contains no Task 05 map tests. This is a coverage gap rather than evidence of Task 05 correctness.

## Verification

- `python3 -m unittest tests.test_sdd_composy_runtime` — 16 tests passed.
- `git status --short` confirms no Task 05 implementation or mapping reference is present.
- `git log -1` — `acf1970 feat(sdd-composy): complete F02 initialization foundation`.
- Reviewed `.planning/power/features/sdd-composy-f02-init-map/task-05-brief.md`, `plan.md`, `plugins/sdd-composy/references/{okf,artifacts,runtime}.md`, and the existing runtime tests.
- Reviewed read-only; no implementation files, HEAD, or commits were changed.

## Required re-review scope

Re-review after the helper, mapping reference, fixture tests, and implementation report exist. The next pass must exercise a temporary repository and assert: no traversal or out-of-root reads; no `.env`, credentials, token, key, certificate, or fleet-environment reads; adaptive package/manifest stack and command extraction; domain evidence without architectural inference; source commit and stale-map detection; deterministic byte-stable JSON; OKF v0.2 context concepts; and atomic publication with failure cleanup.
