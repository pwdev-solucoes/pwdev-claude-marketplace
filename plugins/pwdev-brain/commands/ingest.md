---
description: INGEST — leva uma fonte para raw/, extrai pontos via subagente, discute com o usuário e integra à wiki
argument-hint: "<arquivo em raw/ | caminho externo | URL>"
---

# /pwdev-brain:ingest

Princípio: **o comando conversa, o subagente grava**. A discussão exigida
pela spec acontece aqui na sessão principal; a leitura pesada da fonte e a
escrita na wiki ficam no subagente `brain-ingestor`, em duas passadas.

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Gate
Sem `.claude/pwdev-brain-context.md` ou sem `<brain>/wiki/index.md` válido →
**aborte** e aponte `/pwdev-brain:init`.

## STEP 1 — Normalizar a fonte
`$ARGUMENTS` (se vazio, pergunte o que ingerir):

- **Arquivo já em `raw/`** → usar como está.
- **Caminho externo** → copiar para `<brain>/raw/<nome>` (avisar o usuário;
  nunca mover nem alterar o original).
- **URL** → WebFetch e salvar como `<brain>/raw/<slug>.md` com cabeçalho de
  proveniência (URL canônica e data de captura ISO 8601).

`raw/` é imutável: arquivo que já existe lá **nunca** é editado ou
sobrescrito — nome em conflito ganha sufixo.

## STEP 2 — Passe extract (subagente)
Despache `brain-ingestor` com:

```
LANGUAGE: {{lang}}
MODE: extract
BRAIN_PATH: {{caminho absoluto}}
SOURCE_FILE: {{raw/arquivo}}
HANDOFF_FILE: .claude/pwdev-brain/ingest-{{YYYY-MM-DD}}-{{slug}}.md
USER_ACTOR: human:{{id}}
PROCESS_ACTOR: pwdev-brain/1.0.0
```

Ele lê a fonte inteira + `wiki/index.md` + conceitos relacionados e grava a
**proposta** no HANDOFF_FILE — nada é escrito em `wiki/` nesta passada.

## STEP 3 — Discussão (o coração da operação)
Apresente a proposta ao usuário conforme a preferência do contexto:

- **ponto-a-ponto** — cada ponto extraído: aprovar / editar / descartar.
- **lote** — a lista completa de uma vez, com aprovação única e ajustes.

Registre cada decisão na seção `## Decisões` do HANDOFF_FILE (aprovado /
editado com o novo texto / descartado). Pontos que o usuário **confirmar
como corretos** podem receber `verified` — marque isso explicitamente.

## STEP 4 — Passe apply (subagente)
Despache `brain-ingestor` de novo, mesmo bloco de entrada com
`MODE: apply`. Ele grava/atualiza conceitos, links, `wiki/index.md` e
`wiki/log.md` seguindo estritamente as decisões do handoff.

## STEP 5 — Fechamento
1. Resuma o retorno do subagente para o usuário.
2. Apague o HANDOFF_FILE — o registro durável é o `wiki/log.md`.
3. Se a ingestão tocou muitos conceitos existentes, sugira
   `/pwdev-brain:lint`.

## Saída
```
pwdev-brain — INGEST {{fonte}}

Fonte       raw/{{arquivo}} {{(copiada | capturada de URL | já presente)}}
Conceitos   {{n}} criados · {{n}} atualizados · {{n}} pontos descartados
Ligações    {{n}} links entre conceitos · {{n}} citações em sources
Registro    wiki/log.md — entrada de {{YYYY-MM-DD}} gravada

Sugestão: {{/pwdev-brain:lint (muitas páginas tocadas) | —}}
```
