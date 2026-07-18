# Language Protocol (STEP 0)

Every pwdev-prd command runs this as **STEP 0**, before any other step.

## Resolution Order (silent — all commands except `init`)

1. Read `.planning/config.json` → `lang` field. If valid (`pt-BR` or `en`) → use it silently and continue the command flow.
2. If unset, detect the language of `$ARGUMENTS` (when the command receives arguments): Portuguese → suggest `pt-BR`; English → suggest `en`; ambiguous, empty, or no arguments → ask (step 3).
3. Ask the user:

   ```
   Em qual idioma deseja seguir? / Which language would you like to use?

   1. Portugues (PT-BR)
   2. English (EN)
   ```

   Wait for the answer before proceeding.
4. Save the choice by merging `"lang": "<value>"` into `.planning/config.json` (never overwrite other fields).
5. Confirm briefly (first setup only):
   - `pt-BR`: "Idioma definido: **Portugues (PT-BR)**. Prosseguindo..."
   - `en`: "Language set: **English (EN)**. Proceeding..."

## Special behavior: `/pwdev-prd:init`

`init` **always** asks the user to choose or confirm the language, even when
`config.json` already has one (shows the current value, asks confirm/change).

## Application Rules

Once `{{LANG}}` is resolved:

- **All user-facing output** follows `{{LANG}}`: questions, summaries, confirmations, errors.
- **Generated documents** (plans, reports) follow `{{LANG}}`.
- **Technical terms** stay in English: API, CRUD, REST, endpoint, middleware, deploy, commit, merge, pipeline, etc.
- **File names** stay in English: `plan.md`, `codebase.md`, `config.json`, etc.
- **Code comments** follow the project's existing convention (check CLAUDE.md or existing code).
- **Structured data keys** stay in English.
- **Subagent spawns**: always pass the resolved language in the spawn prompt (`LANGUAGE: {{LANG}}`).

## Mid-conversation override

If the user switches language mid-conversation, acknowledge and ask whether to
update the preference; if confirmed, update `.planning/config.json`.

## Shared config note

`.planning/config.json` is shared with other PWDEV plugins (pwdev-code) —
the same `lang` applies across them; merge, never overwrite.
