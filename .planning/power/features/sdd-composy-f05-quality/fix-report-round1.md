# F05 adversarial correction — round 1

## Finding addressed

The evidence root was resolved before symlink validation, allowing a caller-supplied
symlink root to be silently canonicalized.

## Correction

- Added `_evidence_root()` to inspect the raw root path before resolution.
- Rejects the evidence root itself and caller-controlled intermediate symlink components.
- Preserves the platform `/var` compatibility alias used by macOS temporary directories.
- Routed both `_safe()` and `discover()` through the guard.
- Added regression coverage for direct and intermediate symlink roots.

## Verification

```text
python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -q
Ran 162 tests in 1.543s
OK

git diff --check
exit 0
```

No commit was created.
