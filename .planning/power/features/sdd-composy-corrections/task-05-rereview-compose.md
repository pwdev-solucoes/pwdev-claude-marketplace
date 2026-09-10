# Task 05 — independent Compose producer rereview

SPEC: FAIL

QUALITY: FAIL

FINDINGS:

1. **Important — v1 migration can publish a schema-invalid Compose digest.** The changed migration path in `plugins/sdd-composy/scripts/fleet/run.sh` checks only that `compose_sha256` is a string when `compose_allocated` is true. It does not enforce the v2 schema's `^[a-f0-9]{64}$` constraint and does not validate the completed record against that schema before the atomic replacement. Consequently, a legacy record with `compose_allocated: true` and `compose_sha256: "x"` is accepted and published as schema v2 even though `fleet-member.schema.json` rejects it. The migration test exercises only `compose_allocated: false`, so this producer failure is uncovered. Require the exact digest pattern (and preferably validate the assembled record before publication), then add true/invalid/valid digest migration cases.

Confirmed producer behavior outside that finding:

- Normal `launch.sh --compose` records `.planning/sdd-composy/fleet/<fleet-id>/docker-compose.yml`, exactly the repository-root-relative path copied and supplied to `docker compose -f`.
- Normal Compose launch sets `compose_allocated: true` and records the SHA-256 of that central file before provider dispatch.
- Normal non-Compose launch sets `compose_allocated: false`, omits `compose_sha256`, and still emits a record accepted by schema v2.
- Member ownership, branch, worktree, repository root, port, Compose project, and central Compose path are internally coherent in the launch output.
- The schema requires the allocation boolean and conditionally requires a 64-character lowercase hexadecimal digest when allocated.
- Failure during Compose startup rolls back the producer-created records and bookkeeping; no successfully published allocation remains.

Verification evidence:

- `bash -n plugins/sdd-composy/scripts/fleet/launch.sh plugins/sdd-composy/scripts/fleet/run.sh` — PASS.
- `python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_fleet_runner tests.test_sdd_composy_runtime_adapters tests.test_sdd_composy -v` — PASS (121 tests in 17.858s).
- `git diff --check dbd05f6..5999fa1` — PASS.

REVIEW: REJECTED

The normal launcher producer contract is corrected, but the same reviewed diff extends the migration producer and allows it to publish a record that contradicts schema v2. This Important finding must be resolved before the Compose producer change is accepted. Per review scope, no teardown consumer behavior was evaluated.
