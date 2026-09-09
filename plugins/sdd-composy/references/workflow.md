# SDD Composy workflow contract

This is the portable workflow contract shared by every supported runtime. It defines artifact-driven behavior only; provider commands, tool selection, prompts, and orchestration belong to runtime adapters.

## Language and artifact routing

`/sdd-composy:init` is the only stage that asks for the artifact language. It accepts
exactly `pt-BR` or `en-US` and persists the choice in
`.planning/sdd-composy/config.json`. If no choice is supplied, init returns both choices
and creates no artifacts. Every downstream stage reads that persisted `language` value and
continues without prompting; before init it returns the machine response
`{"status":"not_initialized","next_action":"run_init"}`.

The selected language routes only human-facing artifact prose: PRDs, stories, TechSpecs,
task descriptions, QA/evidence reports, status summaries, and other generated Markdown may
be written in Portuguese (Brazil) or English (United States). Machine keys, IDs, schemas,
filenames, lifecycle values, and command names remain in English in both routes. This keeps
the same contracts portable between Claude Code and Codex while allowing the project team
to read its artifacts in the language selected at initialization. Invalid language values
fail without mutation.

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

`LOOP` repeats the task-level `EXECUTE -> QA -> EVIDENCE (when required) -> REVIEW -> VERIFY` sequence. Its default maximum is 3 iterations. It stops on completion, iteration cap, missing progress, scope expansion, architectural ambiguity, destructive action, external authorization, unrecoverable environment failure, or cancellation. Resume from the last durably published successful stage.

`FLEET` may run only independent ready tasks with complete dependencies, explicit acceptance criteria, known verification commands, and no known overlapping paths. Each task runs in an isolated Git worktree. Integration and merge are separate, explicitly authorized human actions.

## Portable resumption

The durable human contracts and operational state are the source for resumption. A runtime reads and validates them, determines the exact next valid action, and publishes successful transitions before reporting progress. Switching runtimes must not alter lifecycle meaning or repeat a successfully published stage.
# Runtime Hermes

Quando executado no Hermes Agent, o plugin usa `.hermes-plugin/__init__.py` para registrar as
skills e o hook `pre_llm_call`. O runtime deve ser declarado como `hermes`; qualquer divergência
de runtime deve interromper a execução. O bootstrap não substitui os contratos, schemas ou gates
do fluxo compartilhado.
