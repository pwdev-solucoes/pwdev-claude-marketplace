# F02 Task 03 — Safe initialization helper

## STATUS

PASS

## Scope

Implemented `plugins/sdd-composy/scripts/sdd_init.py` with dependency-free
`inspect`/`plan`/`apply`/`verify` commands. Initialization renders the approved
governance templates, creates the OKF v0.2 `tasks/index.md` bundle root with an
actor ID, safely creates `.claude -> .agents`, refuses unsafe symlink and path
collisions, preserves existing files, and uses same-directory atomic no-overwrite
file publication. Plans emit a deterministic digest token; applying a plan with
conflicts requires that exact token.

Added temporary-repository tests covering clean init, actor/index creation,
idempotence, file and directory conflicts, exact-token enforcement, and unsafe
symlink refusal.

## Verification

`python3 -m unittest tests.test_sdd_composy_runtime` — 16 tests passed.

Review follow-up tightened `verify` to parse the exact reserved index
frontmatter (`type`, `okf_version`, `generated.by`, and timestamp), verify all
four installed rule files, and require a non-dangling `.claude` symlink whose
target is exactly `.agents`. Added regression coverage for malformed actor
metadata, missing rules, wrong links, destination directories, saved conflict
tokens across clock changes, parent symlinks, and atomic temporary-file cleanup
under an injected publication failure.

Round-2 review follow-up also requires the reserved index top-level
`actor_id` to exactly match the configured actor, with negative coverage for
both mismatch and missing-field cases.

No environment, credential, or secret files were read. Existing unrelated
worktree changes were preserved.
