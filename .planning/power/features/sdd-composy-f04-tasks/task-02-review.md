# Task 02 review

STATUS: rejected

## SPEC

Task 02 requires `import`, `list`, and `show` over the F01 task schema, stable IDs,
unknown-field preservation, unsafe-path rejection, deterministic serialization, and
same-directory atomic publication. Lifecycle/dependency transitions are explicitly
Task 03 scope and are not evaluated here.

## QUALITY

The focused suite passes (`python3 -m unittest tests.test_sdd_composy_tasks`, 3
tests), and the implementation is small and readable. JSON publication uses a
same-directory temporary file, fsync, and replace; import merges existing task and
top-level fields, and output uses sorted keys. However, the claimed safety boundary
is incomplete and schema validation is weaker than the published schema.

## FINDINGS

1. **P1 — import output is not repository-bound.** `import_tasks()` accepts an
   arbitrary `output` path and never uses its `root` validation parameter (line 26)
   or checks that the output is beneath the task repository. The CLI therefore can
   overwrite any user-selected JSON path, including outside the repository. This
   contradicts the F04 safety contract and the report's “repository-relative
   allowlist validation” claim. Add an explicit repository-root argument/derivation,
   reject absolute/`..` output paths and symlink escapes, and test the rejection
   before any write.

2. **P2 — `updated_at` is not schema-verified.** Validation only checks that it is a
   non-empty string, while `schemas/tasks.schema.json` requires `format:
   date-time`. Malformed persisted state is accepted by `load`, `list`, and `show`.
   Validate the required ISO timestamp shape (and reject invalid dates if practical).

3. **P2 — focused tests do not cover the Task 02 acceptance claims.** The three
   existing tests only cover templates. There are no executable tests for import,
   stable IDs, unknown fields, unsafe output/path handling, deterministic output, or
   atomic failure cleanup. Add those fixtures before marking complete.

## REVIEW

Task 02 is not approved. Task 03 transitions remain correctly absent and should stay
out of scope. Resolve the repository-bound output issue and timestamp validation, add
the focused runtime tests, then request re-review.
