# F02 Task 05 — Codebase map helper

## STATUS

PASS — review round 1 fixes applied

## REPORT

Implemented the read-only `sdd_map.py` inventory and `references/mapping.md`.
The mapper detects languages and common manifests, derives declared commands
without executing them, records filesystem-backed modules/boundaries and low-
confidence domain evidence, records the source Git commit, reports map
staleness, and emits deterministic JSON. It writes OKF v0.2 context concepts
for project, stack, domain, and pitfalls when requested.

Secret/environment-like paths are excluded before opening files, including
`.env*`, credentials, tokens, passwords, private keys, certificates, and fleet
environment files. Published JSON is written atomically and output paths are
repository-bound. External symlinked files and directories are skipped
lexically without resolving outside the repository. All companion OKF context
documents use same-directory temporary files with cleanup on publication
failure.

## Verification

```text
python3 -m unittest tests.test_sdd_composy_runtime
.........
OK

python3 plugins/sdd-composy/scripts/sdd_map.py --repo-root .
emitted schema sdd-composy.codebase, current source commit, commands, and observation_only=true

git diff --check
passed
```

Review-round regressions cover external symlinks and injected companion
publication failure/temporary-file cleanup.

## COMMITS

None. No commit was created because the task brief does not explicitly
authorize committing.

## NOTE

The requested `task-05-brief.md` was not present in this checkout; the
implementation follows the tracked F02 plan/spec and Task 01 report. No secret
or environment file was read.
