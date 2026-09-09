---
type: REFERENCE
okf_version: "0.2"
title: Semantic trace
status: APPROVED
source: sdd-composy
verified: 2026-09-09
---

# Semantic trace

`scripts/sdd_trace.py` records successful semantic actions as append-only JSONL at
`trace/events.jsonl`. The file is never edited or repaired automatically. Use
`record(root, event)` only after the represented action succeeds; `enabled=False`
is a no-op. Events must contain a safe actor, type, stage, optional task ID, and
small structured data. Prompts, output dumps, environment values, models, secrets,
and private paths are prohibited.

`events`, `summary`, and `verify` are read-only queries. Invalid JSONL, symlinked
roots/targets, unsafe paths, invalid sequences, and prohibited fields fail closed.
The trace directory is mode 0700 and the JSONL file mode 0600.
