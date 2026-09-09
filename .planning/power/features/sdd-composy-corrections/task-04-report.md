# Task 04 — implementation report

Status: IMPLEMENTED
Date: 2026-09-09

## Scope and ruling

Implemented only the five declared task files. The runtime adapters delivered here are Hermes
and Codex. Claude remains assigned to Task 06. No `hermes run`, Hermes Kanban, unrecognized
bypass, automatic `--yolo`, or full init-body injection was introduced.

## Baseline

Before execution, the worktree had an existing modification in
`tests/test_sdd_composy_hermes.py` and untracked planning artifacts. The existing test change was
preserved and excluded from this task's commit. The five Task 04 implementation paths had no
pre-existing worktree modifications; two of them did not yet exist.

## TDD evidence

- RED: `python3 -m unittest tests.test_sdd_composy_runtime_adapters -v` failed because
  `plugins/sdd-composy/scripts/loop-engine-hermes.py` did not exist.
- GREEN: the same command passed 7 tests. The fake providers exercise argv/cwd capture, Codex
  JSONL with a distinct final result, strict Hermes JSON, non-zero exit, unavailable executable,
  malformed response, timeout, quoted/metacharacter prompt, mismatched stage, and false VERIFY.
- Regression: `python3 -m unittest tests.test_sdd_composy_loop -v` passed 35 tests.
- Static verification: `bash -n plugins/sdd-composy/scripts/fleet/engine-hermes.sh`, Python
  compilation with a temporary pycache, and `git diff --check` passed.

`tests.test_sdd_composy_hermes` has one expected stale assertion requiring the removed literal
`hermes run`. Per the approved plan, that pre-existing file is preserved in Task 04 and its
semantic rewrite is assigned to Task 08.

## Result

- Codex uses `--sandbox workspace-write` and an exclusive `--output-last-message` file; JSONL
  stdout events are not parsed as the final result.
- Hermes uses `hermes -z PROMPT --in WORKTREE` and refuses automated execution unless isolation
  is confirmed or specific automation consent is supplied.
- Both LOOP adapters return and validate exactly `stage/status/message/verdict/evidence`, expose
  explicit timeout/process/unavailable/malformed-output errors, bind results to the requested
  stage, and reject a successful VERIFY lacking structured successful command evidence.
- Hermes bootstrap registers the 17 skills using `Path` in original or flattened layout and
  injects a small routing orientation on the first turn without triggering work.

## Review round 1

Status: IMPORTANT_FIXED; MINOR_DEFERRED_AS_DIRECTED.

- RED: the new canonical `VERIFY` tests errored because `validate_result` could not receive the
  repository and stage-contract context needed to resolve durable evidence.
- GREEN: `python3 -m unittest tests.test_sdd_composy_runtime_adapters -v` passed 8 tests.
- Regression: `python3 -m unittest tests.test_sdd_composy_loop -v` passed 35 tests.
- Both adapters now resolve the single active LOOP for the stage task, require a regular confined
  non-symlink command-record file, validate its reference SHA-256, task/loop identity, passing
  integer exit code, output SHA-256, and timestamps after REVIEW and before the current deadline.
- A provider-created in-memory `command_record` is rejected even when it claims a passing command.
  The valid regression uses the exact uppercase `VERIFY` emitted by `sdd_loop.orchestrate`.
