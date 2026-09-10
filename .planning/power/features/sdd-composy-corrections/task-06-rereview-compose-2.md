# Task 06 — Compose project ownership rereview

SPEC: PASS

QUALITY: PASS

FINDINGS:

None.

The reviewed change resolves the prior Critical finding. For an allocated resource, teardown now derives `expected_project="sdd_fleet_$fleet"` and compares it with the nested ownership record before validating the digest or invoking Docker. A foreign project therefore cannot redirect the destructive shutdown operation.

Reproduction and verification:

- Independent temporary reproduction with an otherwise valid central file, path, digest, repository root, owner, member, branch, and worktree but `compose_project: "foreign-project"` — rejected before Docker; the Docker log was absent and member metadata plus recoverable worktree remained present.
- Independent temporary reproduction with `compose_project: "sdd_fleet_demo"` — PASS; Docker received `--project-name sdd_fleet_demo` and the canonical central Compose path, returned success, and the member metadata was removed according to the non-merge teardown contract.
- The same independent matrix reconfirmed wrong path, wrong digest, central symlink, and missing central file fail closed with recovery state preserved.
- Focused foreign/valid-project subprocess regressions — PASS (2 tests).
- `python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_loop -q` — PASS (84 tests in 15.855s).
- `bash -n plugins/sdd-composy/scripts/fleet/teardown.sh` — PASS.
- `git diff --check 1ef7adb..70d1228` — PASS.

REVIEW: APPROVED

The Compose project is now bound to the fleet identity before any Docker call, and both rejection preservation and valid success behavior are covered by fresh execution evidence.
