---
name: sdd-quick
description: Deliver a bounded SDD change through a five-file gate with TDD, evidence, trace, and verified verdict.
---

# `$sdd-quick`

Use this portable skill only for a precise bounded objective. Read the quick
reference and both templates before acting. It is runtime-neutral and may be
invoked by Claude Code or Codex; adapters must remain thin.

## Required protocol

1. Inspect repository instructions and preserve unrelated changes.
2. Reject or `ESCALATE` before edits if more than five implementation files,
   architecture, migration, destructive work, scope change, or unknown verification
   is involved.
3. Create the OKF `QUICK_CONTRACT`, assign a `Q-*` identifier (the Q-ID), and register a normal
   `TASK-*` record using `sdd_tasks.py`; quick work never bypasses task lifecycle gates.
   Use the authoritative side-effect-free gate `scripts/sdd_quick.py` (`evaluate`)
   when a machine-readable eligibility decision is needed.
4. Write and run a failing test before implementation (TDD). If it cannot be run,
   escalate.
5. Implement only within the closed allowed-file list and run the known verification.
6. Collect acceptance evidence, review, and verification. Use `sdd_trace.py` to append
   semantic events only after their actions succeed; never write `trace.json` directly.
7. Create the OKF `QUICK_REPORT`, link all evidence from the bundle index, verify the
   trace and artifact integrity, and publish a `COMPLETE` verified verdict only when
   every gate passes. Otherwise report `ESCALATED`, `REJECTED`, or `CAVEATS`.

## Safety

Never record prompts, output dumps, environment variables, secrets, models, or private
paths. Do not silently expand scope. `CONFIRM-SDD-SYNC` remains mandatory for sync
operations. A quick task is a controlled entry path into the normal SDD flow, not a
shortcut around review, evidence, or verification.
