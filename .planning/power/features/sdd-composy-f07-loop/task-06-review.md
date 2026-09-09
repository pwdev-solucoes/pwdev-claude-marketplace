# Task 06 Review — Loop skill and adapter

## Review scope

Read-only review of the portable `$sdd-loop` skill, Claude command adapter,
Codex metadata, and the associated structural, lifecycle, and runtime tests.

## Findings

- The skill explicitly discloses the default autonomous bound of **3
  iterations** and requires explicit human approval.
- The documented lifecycle is canonical and ordered: `EXECUTE`, `QA`,
  `EVIDENCE`, `REVIEW`, and `VERIFY`.
- Cancellation is exposed through `sdd_loop.py cancel` and the Claude command;
  the runtime makes cancellation durable and prevents subsequent mutation.
- The skill requires fresh `sdd-verify` evidence before completion and rejects
  completion claims based only on phrases or runtime messages.
- Safe-stop behavior is documented for completion, iteration cap, no progress,
  scope expansion, architectural ambiguity, destructive action, external
  authorization, cancellation, and unrecoverable environment failure.
- Provider-specific command vectors remain in the dedicated Codex and Claude
  adapters. The loop skill and Claude command do not duplicate or bypass those
  vectors.
- `agents/openai.yaml` is thin metadata and routes users to `$sdd-loop` with the
  approval, bound, fresh-verification, and safe-stop requirements.

## Verification

```text
python3 -m unittest tests.test_sdd_composy tests.test_sdd_composy_loop
Ran 79 tests ... OK
```

`git diff --check` is clean for the reviewed implementation.

## Disposition

**APPROVED** — Task 06 satisfies its brief and is ready for ledger completion.
