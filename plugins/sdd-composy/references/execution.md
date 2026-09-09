# SDD Composy execution contract

Execution consumes exactly one human-approved task in `ready` state, its Markdown
contract, approved upstream contracts, codebase map, and the declared real
`verification_commands`. It never changes approved requirements, stories,
architecture, acceptance criteria, or scope. A missing or ambiguous input is a
blocker, not permission to infer.

## Preflight and ownership

Before starting, record a deterministic preflight containing task ID, contract
fingerprint, dependency result, approved sources, `allowed_paths`, commands,
environment owner, and intended cleanup. The dependency preflight must prove that
every dependency is `complete`; failures are classified `dependency_missing` and
transition the task to `blocked` with an exact `next_action`. Only the run may
start services it owns; record PID/port/process identity and `cleanup_status`. Never
stop or alter user-owned processes. Environment ownership is explicit:
`environment_owned`, `environment_shared`, or `environment_unknown`; the latter
blocks execution.

## TDD and bounded implementation

Implementation follows TDD: create a failing test first, run it and preserve its
command/output as evidence, implement the minimum change, then run the test
again. Missing RED evidence is `tdd_missing` and blocks the task. Every changed
file must resolve beneath an approved repository-relative `allowed_paths` entry;
violations are `path_violation` and are rejected. Approved contracts are
read-only inputs. No generated evidence may contain secrets, credentials,
private keys, or unredacted environment values.

## Real command evidence

Run each declared command as a real process in the declared environment; do not
replace it with a mock or a claimed result. Record command, working directory,
start/end timestamps, exit code, sanitized stdout/stderr, and SHA-256 digests of
relevant outputs. A non-zero result is `command_failed`; an unavailable command
is `command_unavailable`. Evidence paths are confined relative paths and all
entries use known enums. atomic evidence writes must not mutate the approved
contracts.

## Outcomes and transitions

On successful implementation, fresh commands, cleanup, and evidence, transition
`running -> qa_required`. A QA blocker, failed cleanup, missing evidence, or
environment blocker transitions to `blocked` and records `blocked_reason` and
`next_action`. A scope violation, rejected contract, or unauthorized change
transitions to `rejected` and records `rejection_reason`. Never advance after a
QA or review blocker. The execution result must include task ID, outcome, changed
paths, evidence manifest, environment ownership, cleanup status, transition, and
next permitted action.

The execution contract requires human approval before state-changing execution
and is operationally auditable: each event has an actor,
timestamp, source, status, and trace link. Reports use OKF v0.2 metadata and
separate generation and verification actors. Execution is not complete merely
because a command exited zero; QA, evidence, review, and verification gates
remain authoritative.

The portable reference implementation exposes `sdd_execute.preflight`,
`sdd_execute.run_command`, and `sdd_execute.finish` as the adapter boundary.
Their result fields are `outcome`, `transition`, `reason`, `next_action`, and,
when commands run, `evidence_manifest`; adapters must preserve these fields.
