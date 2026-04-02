# Language Selection Protocol (i18n)

> **INTERNAL REFERENCE** — This file is the canonical specification for the language selection behavior.
> It is NOT shipped with individual plugins. Each plugin has self-contained inline instructions
> derived from this spec. Edit this file to update the spec, then sync to each plugin's commands/agents.

This protocol MUST be executed as **STEP 0** of every command, before any other step.

---

## Resolution Order

1. **Check config file**: Read `.planning/config.json` and look for the `lang` field.
   - If `lang` exists and is valid (`pt-BR` or `en`) → use it silently, skip to the command flow.

2. **Detect from input**: If no config exists, analyze the language of `$ARGUMENTS`.
   - If Portuguese detected → suggest `pt-BR`
   - If English detected → suggest `en`
   - If ambiguous or empty → go to step 3

3. **Ask the user**: Present the choice clearly:

   ```
   Em qual idioma deseja seguir? / Which language would you like to use?

   1. Portugues (PT-BR)
   2. English (EN)
   ```

   Wait for the user's response before proceeding.

4. **Save the choice**: Write (or update) `.planning/config.json`:

   ```json
   {
     "lang": "pt-BR"
   }
   ```

   If the file already exists with other fields, merge — do not overwrite.

5. **Confirm briefly** (only on first setup):
   - `pt-BR`: "Idioma definido: **Portugues (PT-BR)**. Prosseguindo..."
   - `en`: "Language set: **English (EN)**. Proceeding..."

---

## Language Application Rules

Once `{{LANG}}` is resolved:

- **All user-facing output** follows `{{LANG}}`: questions, summaries, confirmations, suggestions, error messages.
- **Generated documents** (PRD, plans, reviews) follow `{{LANG}}`.
- **Technical terms** stay in English regardless of language: API, CRUD, REST, endpoint, middleware, deploy, commit, merge, pipeline, etc.
- **File names** stay in English: `PRD.md`, `codebase.md`, `config.json`, etc.
- **Code comments** follow the project's existing convention (check CLAUDE.md or existing code).
- **Structured data keys** stay in English: `{ "meta": { "product": "..." } }`.

---

## Override

If the user writes in a different language mid-conversation (e.g., switches from Portuguese to English), acknowledge and ask:

- `pt-BR` active, user writes in English:
  "I noticed you switched to English. Would you like to continue in English? (This will update your preference)"

- `en` active, user writes in Portuguese:
  "Percebi que voce mudou para portugues. Deseja continuar em portugues? (Isso atualizara sua preferencia)"

If confirmed, update `.planning/config.json` accordingly.

---

## Special Behavior: `init` Commands

The `init` command of each plugin (`/pwdev-prd:init`, `/pwdev-feat:init`, `/pwdev-uiux:init`, `/pwdev-code:init`) uses a **mandatory** language configuration flow instead of the silent resolution:

- **Always asks** the user to choose or confirm the language, even if `.planning/config.json` already exists.
- This ensures users are aware of the language setting when initializing a new workspace.
- If the config already has a `lang` field, it shows the current value and asks to confirm or change.
- The `init` commands are the **primary entry point** for language configuration.

Other commands use the **silent resolution** (read config → detect → ask only if needed).

---

## Related Protocols

- **Model selection**: See `shared/model-protocol.md` for LLM model configuration.
  Both language and model are stored in `.planning/config.json` and configured during `init`.

---

## Quick Reference for Commands

**For `init` commands** — use the expanded "Language Configuration" block (see each plugin's `init.md`).

**For all other commands** — insert this at the top of the flow:

```markdown
### STEP 0 — Language Selection
Follow the language selection protocol from `shared/i18n-protocol.md`.
Read `.planning/config.json` for the `lang` field.
If not set, detect from $ARGUMENTS or ask the user.
All subsequent output must follow the resolved language.
```
