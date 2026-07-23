# Protocolo de Idioma (STEP 0)

Todo comando do pwdev-youtrack roda isto como **STEP 0**, antes de qualquer outra etapa.

## Ordem de resolução (silenciosa — todos os comandos exceto `init`)

1. Ler `.claude/pwdev-youtrack-context.md` → seção 1, campo **Idioma**.
   Se válido (`pt-BR` ou `en`) → usar silenciosamente.
2. Se ausente, ler `.planning/config.json` → campo `lang` (compartilhado com
   pwdev-code, pwdev-feat e pwdev-devops).
3. Se ainda ausente, detectar o idioma de `$ARGUMENTS`.
4. Se ambíguo ou vazio, perguntar:

   ```
   Em qual idioma deseja seguir? / Which language would you like to use?

   1. Portugues (PT-BR)
   2. English (EN)
   ```

5. Persistir a escolha em `.claude/pwdev-youtrack-context.md` **e** mesclar
   `"lang": "<valor>"` em `.planning/config.json` (nunca sobrescrever outros campos).

## Distinção deste plugin

Conversa, relatório e documentação seguem `{{LANG}}`.

**Nome de tool MCP, query do YouTrack, comando de issue, saída de API e log
nunca são traduzidos.** A query language do YouTrack (`project:`, `#Unresolved`,
`State:`) e comandos como `for me State Fixed` são sintaxe, não prosa.

## Regras de aplicação

- **Termos técnicos** permanecem em inglês: issue, sprint, board, backlog,
  assignee, custom field, work item, tag, draft.
- **Nomes de arquivo** permanecem em inglês: `SKILL.md`, `pwdev-youtrack-context.md`.
- **Chaves de dados estruturados** permanecem em inglês.
- Conteúdo criado NO YouTrack (summary, description, comentário) segue o idioma
  do projeto do usuário — pergunte se houver dúvida, nunca traduza sem pedir.
