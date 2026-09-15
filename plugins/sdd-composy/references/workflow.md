# SDD Composy workflow contract

This is the portable workflow contract shared by every supported runtime. It defines artifact-driven behavior only; provider commands, tool selection, prompts, and orchestration belong to runtime adapters.

## Language and artifact routing

`/sdd-composy:init` is the only stage that asks for the artifact language, exactly `pt-BR` or
`en-US`, and persists it in `.planning/sdd-composy/config.json`. Every downstream stage reads that
value and never prompts; before init it returns `{"status":"not_initialized","next_action":"run_init"}`.
Only human-facing prose is localized: machine keys, IDs, schemas, filenames, lifecycle values, and
command names stay in English in every runtime. Full rules: [language contract](language.md).

## Canonical lifecycle

```text
INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS
                                            |
                              EXECUTE -> QA -> EVIDENCE -> REVIEW -> VERIFY
                                       ^       autonomous LOOP       |
                                       +-----------------------------+
                                            |
                                         COMPLETE
```

- `INIT` establishes missing governance and operational files without overwriting existing governance.
- `MAP` records evidenced project, stack, domain, command, convention, and pitfall context.
- `PRD` defines requirements (`RF-*`) and acceptance criteria (`CA-*`).
- `STORIES` refines an approved PRD into stories (`US-*`) and scenarios (`SC-*`). It is required for user-facing behavior and externally consumed APIs. Pure internal work may record `NOT_APPLICABLE` with an explicit justification.
- `TECHSPEC` converts approved product behavior into architecture, interfaces, and test cases.
- `TASKS` produces dependency-aware atomic work contracts and synchronized operational task state.
- `EXECUTE`, `QA`, optional `EVIDENCE`, `REVIEW`, and `VERIFY` implement and challenge one approved task.
- `COMPLETE` is reached only after every applicable gate and completion invariant succeeds.

## Gates and authority

PRD, STORIES when applicable, TECHSPEC, TASKS execution scope, and completion require explicit human approval. Artifact existence, generated metadata, prior summaries, or a runtime's confidence never imply approval. A rejected gate returns control to the artifact that owns the rejected decision; downstream artifacts are then stale until reconciled.

Execution must remain inside the approved requirements, stories, architecture, scope, and task paths. QA and review must have no blocking result. Verification independently reproduces fresh evidence and may reject earlier claims. Completion requires fresh test evidence, an approved verification verdict, and a consistent trace projection.

`EVIDENCE` is required when the approved task contract calls for an acceptance dossier; otherwise the stage may be explicitly recorded as not required. A rejected QA, evidence, review, or verification outcome transitions the task to `rejected`; correction begins only through the guarded `rejected -> ready` transition.

## Human-contract lifecycle vocabulary

PRD, stories, and TechSpec documents use one portable, case-sensitive lifecycle vocabulary:
`DRAFT`, `APPROVED`, `REJECTED`, and `NOT_APPLICABLE`. `DRAFT` pairs with
`human_approval: PENDING` and an empty approval event set. `APPROVED` pairs with
`human_approval: APPROVED` and a matching human `verified` event. `REJECTED` pairs with
`human_approval: REJECTED` and a matching human `verified` event. `NOT_APPLICABLE` is valid
only for the pure-internal stories gate; it pairs with `applicability: NOT_APPLICABLE`, a
non-empty `applicability_justification`, `human_approval: APPROVED`, and a matching human
`verified` event. No runtime may invent aliases such as `VERIFIED` or infer a transition.

## Reduced and concurrent paths

`QUICK` is a bounded reduced path:

```text
SCOPE -> CONTRACT -> IMPLEMENT -> TEST -> REVIEW -> VERIFY
```

It is limited to **5 implementation files**. Before editing, escalate to the full lifecycle if the work crosses that limit or requires architecture decisions, migrations, destructive operations, scope changes, or unknown verification.

`LOOP` repeats the task-level `EXECUTE -> QA -> EVIDENCE (when required) -> REVIEW -> VERIFY` sequence, at most 3 iterations by default, and stops on the terminal reasons defined in [loop.md](loop.md). Resume from the last durably published successful stage.

`FLEET` runs only tasks that pass the admission criteria in [fleet.md](fleet.md), each in an isolated Git worktree. Integration and merge are separate, explicitly authorized human actions.

## Portable resumption

The durable human contracts and operational state are the source for resumption. A runtime reads and validates them, determines the exact next valid action, and publishes successful transitions before reporting progress. Switching runtimes must not alter lifecycle meaning or repeat a successfully published stage.
