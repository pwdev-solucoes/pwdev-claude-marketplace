# PWDEV Flow collaboration contract

Collaboration is an execution optimization, not part of the portable artifact format. The workflow must remain correct when performed by one agent.

## Dispatch policy

- Work inline by default.
- Create collaborating workers only when the user explicitly requests subagents, delegation, or parallel agent work.
- Give each worker one concrete, bounded, independent task.
- Never dispatch two writers against overlapping files.
- Keep human approval and architecture decisions in the primary conversation.
- In plans, `Parallel-safe: yes` expresses file independence; it does not authorize spawning workers by itself.
- Invoking `flow-fleet` or `flow-delegate` is explicit delegation authorization only for the exact command displayed and confirmed by that skill. It does not authorize unrelated subagents, providers, tasks, modes, fleet members, merges, or commands.

## Worker prompt

Every delegated prompt must include:

1. objective and complete acceptance criteria;
2. exact paths to inspect or modify;
3. allowed actions and prohibitions;
4. project instructions to read;
5. verification commands;
6. language;
7. concise return contract.

Workers must not rely on conversation history. Ask them to return evidence and paths, not long duplicated reports.

## Role boundaries

- Research workers inspect and write context; they do not choose architecture.
- Execution workers receive one approved atomic task; they do not redesign scope.
- Advice workers answer one concrete blocker read-only; they do not implement.
- Review workers report findings; they do not silently fix them.
- Verification workers attempt refutation and reproduce commands independently.
- Simplification workers separate proposal analysis from approved application.

The primary agent owns gates, state transitions, scope reconciliation, and final claims.

## Independence

For review and verification, do not show a worker the desired verdict. A review worker receives the diff and contract. A verification worker receives the truths and artifacts but must reproduce evidence independently. The primary agent checks worker claims before presenting a final result.

## Fallback

When collaboration is unavailable or not authorized, execute roles sequentially with explicit lens changes. Do not reduce acceptance criteria or skip independent re-reading merely because only one agent is active.
