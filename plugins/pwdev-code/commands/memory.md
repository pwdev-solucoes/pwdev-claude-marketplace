---
description: Manage curated project memory — capture, list, show, and forget durable decisions, lessons, and conventions
argument-hint: "[capture [decision|lesson|convention] [text] | list [type] | show <name> | forget <name> | link <a> <b> | graph]"
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
| `link <a> <b>` | Add a directed relation a → b (memory graph) |
| `graph` | Show the memory graph (adjacency list + dangling links) |
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
- **`link`** → STEP 7
- **`graph`** → STEP 8
- **empty** → menu:

  **PT-BR:**
  ```
  Memoria do Projeto

  1. capture  — Registrar decisao, licao ou convencao duravel
  2. list     — Listar memorias ativas
  3. show     — Ver uma memoria
  4. forget   — Desativar uma memoria
  5. link     — Relacionar duas memorias (grafo)
  6. graph    — Ver o grafo de memorias

  Escolha (1-6):
  ```

  **EN:**
  ```
  Project Memory

  1. capture  — Record a durable decision, lesson, or convention
  2. list     — List active memories
  3. show     — View one memory
  4. forget   — Deactivate a memory
  5. link     — Relate two memories (graph)
  6. graph    — View the memory graph

  Choose (1-6):
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
6. **Relations**: detect `[[name]]` links in the text and offer any explicit
   `related` names; validate each against the index (active lines only —
   unknown names are dropped with a warning) and consolidate into the
   frontmatter `related:` list.
7. Write `.planning/memory/{type}-{name}.md` in the exact format of
   `references/memory.md` (`source: manual`, `status: active`) and append the
   index line: `` - `{type}` {name} — {description} (memory/{type}-{name}.md) ``,
   adding the `[rel: name1, name2]` suffix when `related:` is non-empty.
8. If active memories > 30 → warn and suggest consolidating.
9. Log: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event memory MEMORY memory_captured "memory/{type}-{name}.md" ""`

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
3. Remove its line from `MEMORY.md`. Do NOT rewrite other lines: `[rel:]`
   entries pointing at the forgotten name become dangling links, which
   selection ignores and `graph` flags.
4. Log: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event memory MEMORY memory_forgotten "memory/{file}" ""`

### STEP 7 — Link
`$2` = `<a> <b>` (two memory names). Adds the directed relation a → b.
1. Validate both names against ACTIVE index lines; missing → list closest names and stop.
2. Add `b` to `a`'s frontmatter `related:` (create the field if absent; no-op if already there).
3. Update `a`'s index line: append/extend the `[rel: ...]` suffix.
4. For a bidirectional relation, run `link b a` too (deliberately explicit).
5. Log: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event memory MEMORY memory_captured "link:{a}->{b}" ""`

### STEP 8 — Graph
Parse ONLY `MEMORY.md`. For each active memory print its adjacency:
```
prefer-postgres-jsonb (decision)
  → service-suffix
  ← referenced by: migrations-need-rollback
```
Then list dangling links (`[rel:]` names with no active index line) with a
hint to `link` or clean them up on the next capture/update of that memory.

## Prohibitions (command-level)
- ❌ NEVER capture without valid name + description + type
- ❌ NEVER duplicate a name (update the existing memory instead)
- ❌ NEVER delete a memory file on forget (status flag + index removal only)
- ❌ NEVER edit MEMORY.md outside the 1-line grammar (the optional `[rel:]`
  suffix always comes last, after the `(path)`)
- ❌ NEVER add a `rel:` entry pointing to a name absent from the index
- ❌ NEVER store secrets or credentials in memories
