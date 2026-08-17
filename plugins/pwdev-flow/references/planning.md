# Planning contract

Planning turns an approved specification into ordered, independently verifiable tasks. Plans may clarify implementation detail but must not weaken acceptance criteria, prohibitions, or definition of done.

## Wave map

Write a dependency map before individual plans. Each wave records:

- `Wave: <number>`;
- `Depends on: <wave numbers or none>`;
- `Complexity: low | medium | high`;
- `Parallel-safe: yes | no`;
- task IDs, file sets, and integration checkpoint.

Mark `Parallel-safe: yes` only when file sets and side effects are disjoint. This field documents independence and does not authorize worker creation.

## Atomic task format

Store `.planning/flow/phases/<slug>/plans/<id>-<task-slug>.md` with:

1. objective and source specification clauses;
2. allowed files, maximum five implementation files;
3. required context paths;
4. exact actions in execution order;
5. acceptance criteria tied to observable behavior;
6. test-first step for every behavior change;
7. exact focused and broader verification commands;
8. stop conditions and prohibitions;
9. dependencies and produced interfaces;
10. expected execution summary path.

Keep at most three tasks in a wave. Split when a task spans unrelated responsibilities, cannot be reviewed independently, or needs more than five implementation files.

## Fix tasks

Correction plans use the same task format, reference the failed truth and evidence, and have high complexity. They may change only what is necessary to resolve the rejection.

## Gate

Present the wave map, file ownership, risks, and verification strategy. Execution starts only after the user approves the plan. When approval changes scope, update both the plan and any affected specification decision before execution.
