# SDD Composy state contract

State is durable, schema-validated, and portable across runtimes. A transition is published only after its prerequisites and represented action succeed.

## Task state machine

```text
pending -> ready -> running -> qa_required -> evidence_required -> review_required -> verify_required -> complete
                      |              |                    |                   |                |
                      +-> blocked     +-> rejected         +-> rejected        +-> rejected     +-> rejected

rejected -> ready
blocked  -> ready
any active state (ready … verify_required) -> blocked | rejected   (with a reason)
any non-terminal state -> skipped                                  (with reason and authority)
```

`skipped` is an additional terminal state and requires an explicit justification. `evidence_required` may be bypassed only when the approved task contract explicitly says no dossier is required; the durable event must record that decision before entering `review_required`.

## Transition guards

| Transition | Required evidence |
|---|---|
| `pending -> ready` | all dependencies are `complete`, contract is approved, acceptance criteria and verification commands are known |
| `ready -> running` | one actor has claimed the task and approved scope is unchanged |
| `running -> qa_required` | implementation is published within allowed paths and focused tests were run |
| `qa_required -> evidence_required` | fresh test evidence exists and QA has no blocking finding |
| `qa_required -> review_required` | the preceding conditions hold and evidence is explicitly not required |
| `evidence_required -> review_required` | the validated criterion-linked evidence dossier is published |
| `review_required -> verify_required` | review has no `BLOCKER` or otherwise blocking finding (severities in `sdd-review`) |
| `verify_required -> complete` | verification independently approves fresh evidence and traceability is consistent |
| applicable active state `-> blocked` | a concrete blocker and exact next human action are recorded |
| gated state `-> rejected` | rejection reason, stale evidence, and producing stage are recorded |
| `rejected -> ready` | correction scope is approved, dependencies remain complete, and stale claims are invalidated |
| non-terminal state `-> skipped` | explicit justification and human authority are recorded |

Gate evidence is recorded with `sdd_tasks.py evidence` (`tests`, `qa`, `review`, `verify`,
`trace`) and moves no state. Freshness is per task and per attempt: entering `running` stamps
`attempt_started_at`, a rejection stamps `evidence_invalidated_at`, and any evidence older than
either is stale. Another task's transition or a re-import never stales it. `verify` and the
`complete` transition apply the same rule.

A task cannot become `ready` before dependencies are complete. A task cannot become `complete` without fresh test evidence, non-blocking QA and review, approved verification, and consistent traceability. `complete` and `skipped` are terminal; reopening requires an explicit new correction or task contract rather than mutating history.

## Workflow and stage persistence

Global state records the active lifecycle stage, active PRD/task, last gate, blockers, loop/fleet summaries, trace health, update timestamp, and exact next valid action. After INIT it is kept current by the mutating CLIs through `scripts/sdd_state.py`: `sdd_tasks.py` (stage, active PRD and task, blockers, next action), `sdd_loop.py` (loop summaries), `sdd_trace.py record` (trace health and event count), and the fleet runner (member summaries). Each update increments `revision` under a lock; an invalid `state.json` fails closed instead of being rewritten. Stage state advances only after its durable output exists and validates. Failed publication leaves the prior state authoritative.

Semantic events are appended after successful actions. The mutable state is current truth, the event log is audit history, and the trace projection is rebuildable query state. No one representation may be rewritten merely to conceal disagreement with another.
