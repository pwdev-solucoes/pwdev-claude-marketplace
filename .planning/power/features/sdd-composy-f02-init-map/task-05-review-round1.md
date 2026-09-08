# Task 05 review — Codebase map helper (round 1)

## Verdict

- SPEC: PASS
- QUALITY: PASS
- Findings: 0 open

## Findings

### [ADDRESSED] Repository-bound inventory crashes on an external symlink

The helper now uses lexical repository-relative paths and excludes symlink files and directories before inventory. The added fixture creates both an external file symlink and an external directory symlink, confirms mapping succeeds, and confirms neither link contributes files or manifests. The original reproduction no longer raises.

### [ADDRESSED] Context publication is only partially atomic

`write_map()` now routes every companion document through `_atomic_write_text()`, which uses a same-directory temporary file, flushes/fsyncs, replaces the destination, and removes the temporary file on failure. The added fixture injects a failure for `stack.md` and confirms temporary files are cleaned up while the already-published `project.md` remains intact. This satisfies the per-document atomic publication contract used by the mapper.

## Verification

- `python3 -m unittest tests.test_sdd_composy_runtime` — 20 tests passed.
- The new fixtures cover external symlink exclusion, per-document temporary publication and cleanup on failure, adaptive language/manifest commands, low-confidence domain evidence, secret exclusion, deterministic in-memory JSON, repository-bound output rejection, and OKF context files.
- Manual read-only reproduction of the former external-symlink failure now succeeds with zero observed files.
- Inspected `task-05-brief.md`, `task-05-report.md`, `references/mapping.md`, F01/F02 artifact/OKF/runtime contracts, `sdd_map.py`, and focused tests.
- No implementation files, HEAD, or commits were changed.
