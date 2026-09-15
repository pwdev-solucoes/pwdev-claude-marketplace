# Semantic trace

`scripts/sdd_trace.py` records successful semantic actions as append-only JSONL at
`trace/events.jsonl`. The file is never edited or repaired automatically. Use
`record <root> --event <file|->` (API: `record(root, event)`) only after the represented action
succeeds; `enabled=False` is a no-op. Recording holds an exclusive lock on
`trace/.events.lock` across read, sequencing, and append, so concurrent writers keep a contiguous
sequence; it also refreshes `trace` in `state.json` when the repository is initialized. Events must contain a safe actor, type, stage, optional task ID, and
small structured data. Prompts, output dumps, environment values, models, secrets,
and private paths are prohibited.

`events`, `summary`, `verify`, `query`, and `verify-projection` are read-only queries; `build`
atomically rebuilds the derived graph projection `trace/trace.json` (which records its source
event count and integrity hash) from `trace/events.jsonl` and a bounded graph input. Invalid JSONL, symlinked
roots/targets, unsafe paths, invalid sequences, and prohibited fields fail closed; the CLI
exits `2` on any error and whenever a verification reports `ok: false`.
The trace directory is mode 0700 and the JSONL file mode 0600.
