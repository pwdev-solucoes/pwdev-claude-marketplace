# Task 06 — independent Compose consumer rereview

SPEC: FAIL

QUALITY: FAIL

FINDINGS:

1. **Critical — `compose_project` is not bound to the fleet identity before destructive shutdown.** `teardown.sh` validates `repository_root`, owner IDs, branch, worktree, the central Compose path, and its hash, but it accepts any non-empty `.resources.compose_project` and passes it directly to `docker compose --project-name ... down`. The producer deterministically owns `sdd_fleet_<fleet-id>`, yet the consumer never checks that value. Independent reproduction changed only the member's nested project to `foreign-project` while retaining the valid central file/path/hash and ownership fields; teardown returned success and invoked `docker compose --project-name foreign-project -f <central-file> down`, then removed the member metadata. A modified or malformed record can therefore target a Compose project not owned by this fleet. Require `compose_project == "sdd_fleet_$fleet"` (or an equivalently strong immutable ownership binding) before Docker invocation, preserve metadata on mismatch, and add a subprocess regression proving Docker is not called.

Confirmed behavior outside that finding:

- Allocated resources resolve exclusively from canonical `repository_root` plus `.planning/sdd-composy/fleet/<fleet-id>/docker-compose.yml`.
- A same-named worktree file is ignored, and legacy top-level mirrors cannot override nested resources.
- `resources.compose_allocated` must be an explicit boolean; `false` skips Docker and `true` requires project, path, and schema-form digest.
- Wrong path, wrong hash, central symlink, and missing central file all fail before Docker and preserve member metadata and the recoverable worktree.
- With correct central path, hash, project, and ownership, successful Docker shutdown removes member metadata while preserving the non-merge worktree/branch as designed.

Reproduction and verification:

- Independent temporary matrix — correct success, wrong path, wrong hash, central symlink, and missing central file: expected behavior PASS; foreign project acceptance: CONFIRMED.
- Focused subprocess tests for central `repository_root`/worktree homonym, legacy mirrors, and explicit allocation flag — PASS (3 tests).
- `python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_loop -v` — PASS (83 tests in 16.601s).
- `bash -n plugins/sdd-composy/scripts/fleet/teardown.sh` — PASS.
- `git diff --check 49dc00a..1ef7adb` — PASS.

REVIEW: REJECTED

The path, digest, symlink, missing-resource, and metadata-preservation corrections work, but destructive Compose project ownership remains forgeable through the member record. This Critical consumer finding must be resolved before approval.
