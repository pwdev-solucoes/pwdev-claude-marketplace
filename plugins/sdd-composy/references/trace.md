# Semantic trace

`scripts/sdd_trace.py` records successful semantic actions as append-only JSONL at
`trace/events.jsonl`. The file is never edited or repaired automatically. Use
`record(root, event)` only after the represented action succeeds; `enabled=False`
is a no-op. Events must contain a safe actor, type, stage, optional task ID, and
small structured data. Prompts, output dumps, environment values, models, secrets,
and private paths are prohibited.

`events`, `summary`, `verify`, `query`, and `verify-projection` are read-only queries; `build`
atomically rebuilds the derived graph projection `trace/trace.json` (which records its source
event count and integrity hash) from `trace/events.jsonl` and a bounded graph input. Invalid JSONL, symlinked
roots/targets, unsafe paths, invalid sequences, and prohibited fields fail closed.
The trace directory is mode 0700 and the JSONL file mode 0600.
