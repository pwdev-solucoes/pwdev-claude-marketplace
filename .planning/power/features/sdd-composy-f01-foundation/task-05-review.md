# Task 05 review — Autonomous, fleet, and evidence schemas

## Verdict

- SPEC: FAIL
- QUALITY: FAIL
- Findings: 2 major

## Findings

### [MAJOR] Evidence entries are not confined to the manifest's PRD

`plugins/sdd-composy/schemas/evidence-manifest.schema.json:7-11,25,29-39` validates `prd_slug` and each evidence `path` independently. It therefore accepts a manifest whose `prd_slug` is `billing-api` while an entry points to `tasks/prd-payments/evidences/output.txt`. That violates the criterion-linked dossier boundary: the entry is syntactically beneath *a* PRD evidence directory, but not beneath the manifest's `tasks/prd-<slug>/evidences/` root. It also leaves the requested cross-field invariant unenforced and permits one PRD's manifest to claim another PRD's evidence. Encode the relationship explicitly (for example by making entry paths relative to the manifest's evidence directory, or by restructuring the document so the PRD prefix is not independently repeatable) and add a fixture that rejects a slug/path mismatch.

### [MAJOR] Evidence path confinement is bypassable with backslash traversal

`plugins/sdd-composy/schemas/evidence-manifest.schema.json:25` rejects only `/../` path segments. A value such as `tasks/prd-billing-api/evidences/..\\secret.txt` therefore matches the schema, but on Windows-compatible path handling resolves outside `evidences/`. This conflicts with the portable Claude Code/Codex contract and the artifact contract's requirement for a confined repository-relative regular-file path. `tests/test_sdd_composy.py:311-314` covers only forward-slash traversal, so it does not expose the bypass. Reject backslashes (or normalize and validate with platform-independent path rules before schema validation) and add invalid fixtures for backslash traversal and other alternate separators accepted by supported runtimes.

## Verification

- `python3 -m unittest tests.test_sdd_composy`: 17 tests passed.
- `git diff --check 272622a..b99f169`: passed.
- Inspected `review-272622a..b99f169.diff`, the Task 05 brief/report, Task 02 lifecycle and artifact contracts, and Task 04 schema conventions.
- The schemas otherwise preserve unknown fields, separate evidence `result` from `evidence_type`, use lowercase 64-hex SHA-256 patterns, declare the loop default as 3, encode the documented terminal states, and expose the exact runtime/UI enums.
- No implementation files were changed during review.

## Re-review round 1 — scoped major findings

### Evidence entries confined to the manifest's PRD: ADDRESSED

`review-b99f169..c2984c4.diff` changes evidence entries to forward-slash paths relative to the manifest's own `tasks/prd-<slug>/evidences/` directory. Because entries no longer repeat a repository-root PRD prefix, they cannot select a different PRD root. Focused fixtures accept `runs/test-output.txt` and reject both same-PRD and cross-PRD repository-root paths.

### Portable backslash traversal rejection: ADDRESSED

The evidence relative-path pattern now rejects every backslash, preventing Windows-compatible `..\\` traversal and alternate-separator paths. Focused fixtures reject `..\\report.txt`, `runs\\..\\report.txt`, and `runs\\output.txt`. `python3 -m unittest tests.test_sdd_composy` passes all 17 tests, and `git diff --check b99f169..c2984c4` passes.

This re-review is limited to the two original major findings. No implementation files were changed during re-review.
