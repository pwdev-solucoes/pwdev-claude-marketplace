# Task 07 review

## Scope and evidence

- Brief: `task-07-brief.md`
- Implementation: `plugins/sdd-composy/scripts/sdd_sync.py`
- Tests: `tests/test_sdd_composy_tasks.py`
- Baseline: `9875c7f`
- Focused command: `python3 -m unittest tests.test_sdd_composy_tasks -q` — 22 tests passed.
- `git diff --check` — passed.

## Findings

### Important — explicit authority cannot resolve identity conflicts

`apply()` rejects every plan containing `identity_changed` before applying either
`authority="markdown"` or `authority="json"`. This makes the explicit authority
argument ineffective for one of the synchronization classifications and prevents
the stated Task 07 contract (explicitly selected resolution) from resolving a
changed title/dependencies/acceptance contract. The implementation should either
apply the selected source to the other representation, or expose a separate,
explicit conflict-resolution operation; it must not silently proceed, but the
current unconditional rejection leaves the requested operation unavailable.

### Important — JSON authority cannot resolve JSON-only tasks

The JSON-authority branch only rewrites Markdown files already present in the
Markdown root. If the plan contains a `json_only` item, it leaves that item
unchanged and post-apply verification necessarily fails. The inverse direction
(`markdown_only` under Markdown authority) is supported by merging the Markdown
task into JSON. The two explicit authority choices therefore do not have
symmetrical, verifiable behavior for the supported classifications.

### Minor — no atomic multi-file rollback

Each destination is written through a same-directory temporary file and
`os.replace`, which satisfies per-file atomic replacement. However, a JSON-
authority apply can replace several Markdown files; if a later replacement or
post-write verification fails, earlier replacements remain. If multi-file apply
is intended to be all-or-nothing, stage and verify all outputs before replacing
or provide rollback. This is not a blocker for the focused scope if per-file
atomicity is the chosen contract.

## Positive checks

- Exact `CONFIRM-SDD-SYNC` token is enforced.
- Plan fingerprints are re-read before writes, so stale plans and changed inputs
  are rejected.
- Repository-bound paths, symlink roots, state files, Markdown inputs, and
  destination paths are rejected.
- Unknown JSON top-level/task fields are retained by the Markdown-authority merge.
- Same-directory temporary files are fsynced and atomically replaced.
- Post-apply inspection is performed and failures are surfaced.
- Failure-path tests retain source bytes for the covered cases.

## Verdict

**REJECTED — changes required before Task 07 can be marked complete.** The two
Important findings need implementation and regression tests, followed by a
fresh focused review.
