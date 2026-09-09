# Task 01 review — loop state machine

## Scope

Read-only review of the Task 01 brief/report, `sdd_loop.py`, loop reference/schema,
and the focused test suite. The review checked stage transitions, caps, terminal
reasons, atomic publication, symlink safety, CLI behavior, and immutability after
failure/termination.

## Verification

`python3 -m unittest tests.test_sdd_composy_loop` — 4 tests passed.

## Findings

### Important — loop directory symlinks are not rejected

`_path()` calls `folder.mkdir(parents=True, exist_ok=True)` without checking the
`.planning`, `sdd-composy`, or `loops` components for symlinks. If `loops` (or an
ancestor) is a symlink to another directory, the implementation follows it and
publishes state outside the intended repository location. The brief/report claim
that loop state symlinks are rejected, but the safety boundary must cover the
directory chain as well as the final JSON path.

### Important — atomic publication does not fsync the containing directory

The temporary file is flushed and fsynced before `os.replace`, but the parent
directory is not fsynced afterward. A crash after rename can therefore lose the
directory entry despite the file fsync, so the stated atomic publication guarantee
is incomplete. The publish path should fsync the directory after replacement (with
an explicit, portable handling for platforms where directory fsync is unavailable).

### Minor — focused tests do not cover the required matrix

The brief requires tests for every stage/legal transition, every terminal reason,
invalid caps, and atomic publication. The current suite has four tests and does not
exercise all terminal reasons, pending validation, directory symlink rejection,
CLI cancel behavior, malformed state, or byte-level immutability on rejected
transitions. Add those tests before considering the task complete.

## Disposition

**REJECTED** pending correction of both Important findings and expansion of the
focused test matrix. The implementation otherwise correctly bounds caps to 1–3,
rejects terminal continuation through the public API, validates terminal metadata,
and uses a temporary file plus fsync before replacement.
