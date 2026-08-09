# Protocolo de Idioma (STEP 0)

Todo comando do pwdev-obsidian roda isto como **STEP 0**, antes de qualquer
outra etapa.

## Ordem de resolução (silenciosa — todos os comandos exceto `init`)

1. Ler `.claude/pwdev-obsidian-context.md` → seção 1, campo **Idioma**.
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

5. Persistir a escolha em `.claude/pwdev-obsidian-context.md` **e** mesclar
   `"lang": "<valor>"` em `.planning/config.json` (nunca sobrescrever outros campos).

## Distinção deste plugin

Conversa, panorama e documentação seguem `{{LANG}}`.

**Nome de tool MCP, chave de query JsonLogic, `targetType`/`scope` e path de
arquivo nunca são traduzidos.** `vault_read`, `{"var": "stat.mtime"}`,
`targetType: "frontmatter"`, `daily/2026-08-09.md` são sintaxe do servidor,
não prosa.

## Regras de aplicação

- **Termos técnicos** permanecem em inglês quando são valores do sistema:
  nomes de tool, operadores JsonLogic (`var`, `and`, `glob`, `regexp`),
  `targetType` (`heading`, `block`, `frontmatter`), `scope`
  (`content`, `marker`, `markerAndContent`, `parent`), `operation`
  (`replace`, `prepend`, `append`, `delete`).
- **Nomes de arquivo** permanecem em inglês: `SKILL.md`,
  `pwdev-obsidian-context.md`.
- **Conteúdo criado NO vault** (título de nota, corpo, frontmatter, tags)
  segue o idioma do vault/usuário — pergunte se houver dúvida, nunca
  traduza sem pedir.
