# Language contract

SDD Composy supports exactly `pt-BR` and `en-US`. `/sdd-composy:init` is the
only entry point allowed to ask for this choice. It persists the choice in
`.planning/sdd-composy/config.json` using an atomic, confined write.

All downstream skills read the persisted `language` value and never prompt.
Before initialization they return the machine response
`{"status":"not_initialized","next_action":"run_init"}`. Invalid values
are rejected without changing the existing configuration. Machine keys, IDs,
schemas, filenames, and command names remain in English; only human-facing
artifact content is localized.
