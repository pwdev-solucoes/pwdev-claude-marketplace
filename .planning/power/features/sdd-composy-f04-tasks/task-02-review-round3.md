# Task 02 review — round 3

STATUS: rejected

## SPEC

RFC3339 validation now requires a `T` time component and `Z`/explicit offset;
imports accept an injectable fixed clock; runtime fixtures cover merge,
determinism, unsafe output/symlink paths, and atomic cleanup. Task 03 transitions
remain out of scope.

## QUALITY

`python3 -m unittest tests.test_sdd_composy_tasks` passes (6 tests). The previous
timestamp and clock-boundary findings are resolved. Repository confinement and
unknown-field preservation remain present.

## FINDINGS

1. **P2 — `list` and `show` CLI behavior is not exercised by runtime fixtures.**
   The test named `test_import_list_show_merge_and_deterministic` only calls
   `sdd_tasks.load()` and inspects the returned dictionary; it never invokes the
   `list` or `show` command paths (lines 105–106). Those paths can regress without
   failing the focused suite. Add subprocess or direct `main()` coverage asserting
   list JSON and show-by-ID JSON, including unknown-ID failure behavior.

## REVIEW

Task 02 is not approved yet due to the untested public `list`/`show` interfaces.
Implementation concerns from rounds 1–2 are resolved. Add the command-path fixtures
and request final review; no Task 03 work is required.
