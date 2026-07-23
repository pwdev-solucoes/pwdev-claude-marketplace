# YouTrack Query Language — Cheat Sheet

A busca do YouTrack usa pares `atributo: valor` separados por espaço (AND
implícito). Vírgula entre valores do mesmo atributo é OR. `-` nega.
Valores com espaço vão entre chaves: `{In Progress}`.

## Atributos essenciais

| Atributo | Exemplo | Nota |
|---|---|---|
| `project:` | `project: ODARA` | nome ou short name |
| `assignee:` | `assignee: me` · `assignee: joao.silva` | `me` = usuário atual |
| `State:` | `State: {In Progress}` · `State: Open` | custom field de estado |
| `priority:` | `priority: Critical` | |
| `type:` | `type: Bug` | |
| `tag:` | `tag: regression` | |
| `reporter:` | `reporter: me` | |
| `created:` | `created: today` · `created: 2026-01-01 .. 2026-07-23` | ranges com `..` |
| `updated:` | `updated: {This week}` | datas relativas entre chaves |
| `resolved date:` | `resolved date: {Last month}` | |
| `summary:` / `description:` | `summary: login` | busca textual no campo |
| `has:` | `has: attachments` · `has: -{Assignee}` | presença de valor |

## Atalhos com `#`

| Atalho | Significado |
|---|---|
| `#Unresolved` / `#Resolved` | estado não resolvido / resolvido |
| `#Open`, `#{In Progress}` | valor de estado direto |
| `#Bug`, `#Critical` | valor de qualquer enum (type, priority…) |
| `#me` | issues relacionadas a mim |
| `#Star` | favoritas |
| `#{Has Assignee}` | tem responsável |

## Datas relativas

`today`, `yesterday`, `{This week}`, `{Last week}`, `{This month}`,
`{Last month}`, e ranges: `created: 2026-07-01 .. 2026-07-23`,
`updated: {minus 7d} .. today`.

## Ordenação

`sort by: {updated} desc` · `sort by: priority asc` — sempre no fim da query.

## Consultas prontas

| Objetivo | Query |
|---|---|
| Minhas issues abertas | `assignee: me #Unresolved` |
| Bugs críticos sem responsável | `type: Bug priority: Critical has: -{Assignee} #Unresolved` |
| Criadas por mim esta semana | `reporter: me created: {This week}` |
| Resolvidas no mês no projeto | `project: ODARA #Resolved resolved date: {This month}` |
| Em progresso, mais recentes primeiro | `#{In Progress} sort by: {updated} desc` |
| Sem atualização há 2 semanas | `#Unresolved updated: * .. {minus 14d}` |
| Issues de um sprint | `Board Nome do Board: {Sprint 12}` |
| Com anexo, taggeadas regression | `has: attachments tag: regression` |
| Comentadas por mim | `commented by: me` |
| Backlog (fora de qualquer sprint) | `Board Nome do Board: -{Sprint *}` ou saved search do board |

## Sintaxe de comandos (endpoint /api/commands e tool de update)

Comandos mudam issues com a mesma linguagem dos atributos, sem `:`.
Exemplos: `for me` (assignee) · `State Fixed` · `priority Major` ·
`tag regression` · `Board Nome do Board Sprint 12` (move para o sprint) ·
`work Today 2h Revisão de código` (log de trabalho).
Combinável: `for joao.silva State {In Progress} tag urgente`.
