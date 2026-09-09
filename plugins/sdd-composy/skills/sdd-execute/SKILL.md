---
name: sdd-execute
description: Execute one approved SDD Composy task with bounded paths, real evidence, and guarded lifecycle transitions.
metadata:
  version: 0.1.0
---

# SDD Execute

Read `references/execution.md`, `references/tasks.md`, `references/states.md`,
`references/safety.md`, and the approved task contract before acting. This skill
is portable across Claude Code and Codex; its adapter only routes requests and
does not reimplement execution policy. The bundled `scripts/sdd_execute.py`
functions `preflight`, `run_command`, and `finish` are the public deterministic
execution boundary; adapters preserve their result fields and do not create
test-only bypasses.

Require exactly one `ready` task and a successful dependency preflight. Require
TDD RED evidence before implementation, enforce the task's allowed paths, and
run every declared verification commands as real commands. Record sanitized
stdout/stderr, exit codes, SHA-256 evidence, environment ownership, and cleanup.
Never modify approved contracts or user-owned processes.

On success, request the guarded `running -> qa_required` transition. A concrete
dependency, environment, QA, evidence, or cleanup blocker becomes `blocked`; a
scope violation or rejected contract becomes `rejected`. Record the exact reason
and next action, and stop on any review/QA blocker. Return the execution result,
evidence manifest, changed paths, ownership/cleanup status, and permitted next
lifecycle action. Do not commit, push, publish, or expose secrets.
Do not read or expose credentials, private keys, certificates, or fleet environment files.
