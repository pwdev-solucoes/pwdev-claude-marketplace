# Protocolo de Idioma (STEP 0)

Todo comando do pwdev-glpi roda isto como **STEP 0**, antes de qualquer outra etapa.

## Ordem de resolução (silenciosa — todos os comandos exceto `init`)

1. Ler `.claude/pwdev-glpi-context.md` → seção 1, campo **Idioma**.
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

5. Persistir a escolha em `.claude/pwdev-glpi-context.md` **e** mesclar
   `"lang": "<valor>"` em `.planning/config.json` (nunca sobrescrever outros campos).

## Distinção deste plugin

Conversa, relatório e documentação seguem `{{LANG}}`.

**Nome de tool MCP, status de ticket, itemtype e chave de filtro JSON nunca
são traduzidos.** `search_tickets`, `status: ["new", "assigned"]`,
`itemtype: "Computer"` são sintaxe do servidor, não prosa.

## Regras de aplicação

- **Termos técnicos** permanecem em inglês quando são valores do sistema:
  statuses (`new`, `assigned`, `planned`, `waiting`, `solved`, `closed`),
  itemtypes (`Computer`, `Monitor`, `Phone`, `NetworkEquipment`), chaves de
  filtro (`urgency`, `impact`, `requester_user_id`).
- **Nomes de arquivo** permanecem em inglês: `SKILL.md`, `pwdev-glpi-context.md`.
- Conteúdo criado NO GLPI (título do chamado, followup, texto de solução)
  segue o idioma da instância/time do usuário — pergunte se houver dúvida,
  nunca traduza sem pedir.
