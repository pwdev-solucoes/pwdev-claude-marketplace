---
description: Manage curated project memory — capture, list, show, and forget durable decisions, lessons, and conventions
argument-hint: "[capture [decision|lesson|convention] [text] | list [type] | show <name> | forget <name>]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# /pwdev-code:memory — Curated Project Memory

## Role
Human-facing utility for the project's curated memory
(`.planning/memory/`, protocol: `${CLAUDE_PLUGIN_ROOT}/references/memory.md`).
Auto-capture from the verify/review loops happens inline in those commands —
this command is for manual curation and consultation.

## Input
`$1` = subcommand, `$2` = rest.

| Subcommand | What it does |
|-----------|-------------|
| `capture [type] [text]` | Create a memory (asks for missing type/text) |
| `list [type\|--all]` | Show the index, optionally filtered (`--all` includes forgotten) |
| `show <name>` | Print one memory file |
| `forget <name>` | Deactivate a memory (file preserved) |
| *(empty)* | Interactive menu |

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Ensure workspace (idempotent)
```bash
mkdir -p .planning/memory
[ -f ".planning/memory/MEMORY.md" ] || printf '# Project Memory Index\n<!-- managed by /pwdev-code:memory — one line per ACTIVE memory; edit via the command -->\n\n' > .planning/memory/MEMORY.md
```

### STEP 2 — Route `$1`

- **`capture`** → STEP 3
- **`list`** → STEP 4
- **`show`** → STEP 5
- **`forget`** → STEP 6
- **empty** → menu:

  **PT-BR:**
  ```
  Memoria do Projeto

  1. capture  — Registrar decisao, licao ou convencao duravel
  2. list     — Listar memorias ativas
  3. show     — Ver uma memoria
  4. forget   — Desativar uma memoria

  Escolha (1-4):
  ```

  **EN:**
  ```
  Project Memory

  1. capture  — Record a durable decision, lesson, or convention
  2. list     — List active memories
  3. show     — View one memory
  4. forget   — Deactivate a memory

  Choose (1-4):
  ```

### STEP 3 — Capture

1. Resolve `type` from `$2` (`decision|lesson|convention`); if missing, ask.
2. Resolve the text; if missing, ask ("What should be remembered? 1-3 lines").
3. Derive `name` (kebab-case slug from the text) and `description` (≤120 chars).
4. **Durability check**: if it only matters for the current phase → suggest
   decisions.md / verify.md instead and stop (memory is durable knowledge).
5. **Dedupe**: grep the index for the name. Exists → show it and ask
   update vs. cancel (update edits the existing file, keeps the index line
   in sync).
6. Write `.planning/memory/{type}-{name}.md` in the exact format of
   `references/memory.md` (`source: manual`, `status: active`) and append the
   index line: `` - `{type}` {name} — {description} (memory/{type}-{name}.md) ``.
7. If active memories > 30 → warn and suggest consolidating.
8. Log: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event memory MEMORY memory_captured "memory/{type}-{name}.md" ""`

### STEP 4 — List
```bash
cat .planning/memory/MEMORY.md
```
Filter by `$2` type if given. With `--all`, also show forgotten ones:
```bash
grep -l "status: forgotten" .planning/memory/*.md 2>/dev/null
```
Present as a table (type / name / description), plus the active count.

### STEP 5 — Show
Match `$2` against frontmatter `name` or file stem; print the file. Not found
→ list closest names.

### STEP 6 — Forget
1. Show the memory and confirm with the human.
2. Set `status: forgotten` in the file's frontmatter (Edit — never delete the file).
3. Remove its line from `MEMORY.md`.
4. Log: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event memory MEMORY memory_forgotten "memory/{file}" ""`

## Prohibitions (command-level)
- ❌ NEVER capture without valid name + description + type
- ❌ NEVER duplicate a name (update the existing memory instead)
- ❌ NEVER delete a memory file on forget (status flag + index removal only)
- ❌ NEVER edit MEMORY.md outside the 1-line grammar
- ❌ NEVER store secrets or credentials in memories
