# Task 05 — Compose producer rereview 2

SPEC: PASS

QUALITY: PASS

FINDINGS:

None.

The reviewed fix closes the prior migration-digest finding:

- An allocated legacy record now requires `compose_sha256` to match the v2 schema's exact lowercase 64-hex form.
- Its `compose_file` must equal the fleet-owned central path `.planning/sdd-composy/fleet/<fleet-id>/docker-compose.yml`.
- Every component of that confined central path is checked for symlinks, and the target must be a regular file.
- The supplied digest must equal the SHA-256 of that exact central file before the migrated v2 record is atomically published.
- The migrated nested `resources` preserves the validated central path, allocation flag, digest, branch, worktree, port, and Compose project; unknown top-level fields remain preserved.

Reproduction and verification:

- `python3 -m unittest tests.test_sdd_composy_fleet_runner.FleetRunnerTest.test_explicit_v1_migration_is_atomic_preserves_extensions_and_validates_terminals -v` — PASS. This test creates the confined central Compose file, proves digest `"x"` is rejected without inode/content replacement, then computes the real file SHA-256 and proves the valid allocated record is accepted, schema-valid, atomically replaced, and bound to the same central file.
- `python3 -m unittest tests.test_sdd_composy_fleet_runner -v` — PASS (9 tests).
- `bash -n plugins/sdd-composy/scripts/fleet/run.sh` — PASS.
- `git diff --check 5999fa1..49dc00a` — PASS.

REVIEW: APPROVED

The prior Important finding is resolved within the requested producer/migration scope. No teardown consumer behavior was evaluated.
