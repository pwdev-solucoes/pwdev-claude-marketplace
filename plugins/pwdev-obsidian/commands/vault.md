---
description: Panorama do vault — estrutura de pastas, tags mais usadas, notas recentes; leitura pura
argument-hint: "[pasta]"
---

# /pwdev-obsidian:vault

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Gate
`vault_list {}` falhou → apontar `/pwdev-obsidian:init` (ou "o Obsidian está
aberto?" se o `check-setup.sh` estiver verde) e parar.

## STEP 1 — Estrutura
`vault_list` na raiz (path vazio). Para as pastas de 1º nível relevantes
(ou só a de `$ARGUMENTS`, se informada), `vault_list` de novo para contar
notas por pasta.

## STEP 2 — Tags
`tag_list` — ordenar por contagem de uso, top 10.

## STEP 3 — Notas recentes
Sem tool dedicada de "listar por data" — usar `search_query` com o truque:

```json
{"var": "stat.mtime"}
```

Todo arquivo com `mtime > 0` é truthy, então o tool devolve
`{filename, result: mtime}` para o vault inteiro. Ordenar o array retornado
por `result` desc no lado do agente e pegar as N mais recentes (ex.: 10).
Se `$ARGUMENTS` indicar uma pasta, combine com `glob` para restringir:

```json
{"and": [{"var": "stat.mtime"}, {"glob": ["{{pasta}}/*", {"var": "path"}]}]}
```

## STEP 4 — Saída
Tabela(s) Markdown:
- Pastas principais + contagem de notas
- Top 10 tags por uso
- 10 notas mais recentes (path + data formatada a partir do `mtime`, que
  vem em milissegundos epoch)

## STEP 5 — Persistir (opcional)
Oferecer salvar o panorama como nota no próprio vault via `vault_write`
(perguntar o path, ex. `_meta/vault-overview.md`) — **só com confirmação
explícita**, e avisar se isso for sobrescrever uma nota já existente.

Panorama é leitura — nenhuma mutação neste comando fora do STEP 5.
