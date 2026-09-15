# Language contract

SDD Composy supports exactly `pt-BR` and `en-US`. `/sdd-composy:init` (the `sdd-init` skill) is
the only entry point allowed to ask for this choice; it persists the choice in
`.planning/sdd-composy/config.json` with an atomic, confined write. Invalid values are rejected
without changing the existing configuration.

## Consuming the language in every other skill

Before writing human-facing prose, run `scripts/sdd_language.py <repo-root>` and consume only the
persisted `language`. If the result is `not_initialized`, return it unchanged with
`next_action: run_init`: never ask for a language elsewhere and never write artifacts before
initialization. Read-only operations that emit no human prose (trace queries, sync inspection,
fleet status) do not need the language.

## What is localized

- `pt-BR`: write human narrative, summaries, descriptions, and labels in Brazilian Portuguese;
  `en-US`: in English. This covers PRDs, stories, TechSpecs, task descriptions, QA and evidence
  reports, status summaries, and every other generated Markdown.
- When rendering a template, translate its placeholder prose but preserve IDs, schema keys, enum
  values, lifecycle values, filenames, commands, and parser-required headings.
- Never translate user evidence (command output, quoted logs, file contents) or machine keys.
