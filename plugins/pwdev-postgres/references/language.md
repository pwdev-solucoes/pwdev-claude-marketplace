# Protocolo de Idioma (STEP 0)

Todo comando do pwdev-postgres roda isto como **STEP 0**, antes de qualquer
outra etapa.

## Ordem de resolução (silenciosa — todos os comandos exceto `init`)

1. Ler `.claude/pwdev-postgres-context.md` → seção 1, campo **Idioma**.
   Se válido (`pt-BR` ou `en`) → usar silenciosamente.
2. Se ausente, ler `.planning/config.json` → campo `lang` (compartilhado com
   os demais plugins pwdev).
3. Se ainda ausente, detectar o idioma de `$ARGUMENTS`.
4. Se ambíguo ou vazio, perguntar:

   ```
   Em qual idioma deseja seguir? / Which language would you like to use?

   1. Portugues (PT-BR)
   2. English (EN)
   ```

5. Persistir a escolha em `.claude/pwdev-postgres-context.md` **e** mesclar
   `"lang": "<valor>"` em `.planning/config.json` (nunca sobrescrever outros
   campos).

## Distinção deste plugin

Conversa, relatório e documentação seguem `{{LANG}}`.

**Nome de tool MCP, palavra-chave SQL, tipo de dado e chave de parâmetro JSON
nunca são traduzidos.** `run_select`, `confirm: true`, `where`,
`add_column`, `TEXT`, `TIMESTAMPTZ` são sintaxe do servidor/do Postgres, não
prosa.

## Regras de aplicação

- **Termos técnicos** permanecem em inglês quando são valores do sistema:
  ações de `alter_table` (`add_column`, `drop_column`, `rename_column`,
  `set_default`, `set_nullable`), chaves de parâmetro (`table`, `schema`,
  `where`, `set`, `values`, `confirm`, `cascade`), modos de resposta
  (`preview`, `executed`).
- **SQL não se traduz** — identificadores, tipos e statements ficam como o
  banco espera.
- **Nomes de arquivo** permanecem em inglês: `SKILL.md`,
  `pwdev-postgres-context.md`.
- Nomes de tabelas/colunas criados NO banco seguem a convenção do projeto do
  usuário — pergunte se houver dúvida, nunca invente convenção.
