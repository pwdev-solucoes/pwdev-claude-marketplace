# Task 07 review

## Disposition

**REJECTED — important finding requires correction before F05 proceeds.**

## Verification

Command run:

```text
python3 -m unittest tests.test_sdd_composy_quality.EvidenceManifestContractTest -v
```

Result: 3 tests passed. `git diff --check` was not run because this review is read-only.

The implementation covers direct traversal/absolute/backslash paths, direct symlinks,
missing files, enum validation, result/type separation, SHA-256 generation and checking,
HTML escaping, and the requested missing-screenshot PDF failure path.

## Findings

### F05-T07-001 — Important: nested symlink components are accepted

`_safe()` rejects a candidate when the final path itself is a symlink, and rejects a
resolved path outside the evidence root. It does not reject a symlink in an intermediate
component when that link resolves back inside the root. For example, with `alias -> real`
inside the root, `alias/x.txt` is accepted and hashed. This violates the brief/reference
requirement that evidence paths reject symlinks and leaves the manifest dependent on a
mutable indirection. Walk every path component (or compare each component with `lstat`)
and fail closed for any symlink before reading or hashing. Add a regression test for an
internal directory symlink and exercise it through build and verify.

### F05-T07-002 — Important: required test matrix is not present

The task brief explicitly requires failing tests for path traversal, symlinks, unknown
enums, result/type separation, missing files, HTML injection, hashes, and unloaded PDF
images. The delivered quality tests cover only three grouped cases and do not test
`verify()` missing/hash failure outputs, nested symlinks, manifest/output confinement,
deterministic ordering, or successful HTML export. Add focused tests for each contract,
including the nested symlink case above, before marking the task complete.

## Review conclusion

Do not advance the task or claim completion until T07-001 is fixed with root-cause
coverage and the missing contract tests are added and pass.
