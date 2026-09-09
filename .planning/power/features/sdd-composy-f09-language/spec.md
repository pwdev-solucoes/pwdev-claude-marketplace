# SDD Composy F09 — Language-aware artifacts
Status: DRAFT
Source: User request to ask for language when omitted and generate artifacts in PT-BR.
Updated: 2026-09-09

## Problem
SDD Composy documentation is bilingual, but artifact generation has no persisted language contract. When no language is supplied, generation must ask instead of silently choosing a default.

## Approach
Persist a validated workspace language (`pt-BR` or `en-US`) during initialization. Only `init` asks the user to choose the language. Every other artifact-producing skill reads that persisted preference and never prompts; if the workspace has not been initialized, it fails with an actionable initialization error.

## Decisions
- Decision: supported values are exactly `pt-BR` and `en-US`. Choice: fixed enum. Why: deterministic cross-runtime behavior. Trade-off: other locales require a later extension. Reversible: yes.
- Decision: only init may prompt for language. Choice: downstream skills are read-only consumers of init configuration. Why: one configuration authority and predictable automation. Trade-off: using artifact skills before init fails instead of prompting. Reversible: yes.
- Decision: schemas, IDs, keys, filenames, commands, and machine enums remain English. Choice: localize human-facing labels/content only. Why: compatibility. Trade-off: mixed-language artifacts. Reversible: yes.
- Decision: existing persisted language wins when no explicit override is supplied. Choice: preserve workspace preference. Why: stable resumes. Trade-off: changing language requires explicit update. Reversible: yes.

## Interfaces
- `sdd_init.py ... --lang pt-BR|en-US` persists language.
- `sdd_init.py ... --lang pt-BR|en-US` persists the choice; when omitted, init returns structured choices for the user.
- Shared language resolver returns `{language, source}` to downstream skills or `{status: "not_initialized", next_action: "run_init"}`.

## Constraints
- Never generate artifacts before language is resolved.
- Never translate machine keys, IDs, schemas, filenames, or command names.
- Invalid language values fail without mutation.
- All writes remain atomic and path-confined.

## Out of scope
New locales, automatic translation of existing artifacts, and changing historical artifacts without an explicit migration.

## Acceptance criteria
- Init asks when language is omitted and no preference exists.
- Explicit `--lang` persists and is reused by later skills.
- Explicit override is validated and atomic.
- Non-init skills never prompt and use only init configuration.
- PT-BR and EN-US human-facing templates are selectable.
- Claude and Codex routes expose the same behavior.
- Tests cover missing, valid, invalid, persisted, override, fallback, and no-write cases.
