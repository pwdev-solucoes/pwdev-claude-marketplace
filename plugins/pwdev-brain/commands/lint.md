---
description: LINT — valida conformidade OKF e saúde da wiki via subagente; aplica só as correções aprovadas
argument-hint: "[--fix]"
---

# /pwdev-brain:lint

Padrão em duas passadas: **reporta sempre; aplica só o aprovado.** O
subagente `brain-linter` valida contra
`${CLAUDE_PLUGIN_ROOT}/references/lint-rules.md`.

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Gate
Sem `.claude/pwdev-brain-context.md` ou sem `<brain>/wiki/index.md` válido →
**aborte** e aponte `/pwdev-brain:init`.

## STEP 1 — Passe report (subagente)
Despache `brain-linter` com:

```
LANGUAGE: {{lang}}
MODE: report
BRAIN_PATH: {{caminho absoluto}}
REPORT_FILE: .claude/pwdev-brain/lint-{{YYYY-MM-DD}}.md
```

Ele varre a wiki e grava o relatório ranqueado (erro → aviso → info), cada
finding no formato `[BR-nnn] … auto-fixável: sim|não · fix: …`. Nada é
corrigido nesta passada.

## STEP 2 — Revisão
Apresente os findings ranqueados. O usuário marca o que aprovar. Regras:

- **BR-3xx** (staleness, contradições, lacunas) nunca são auto-fix — viram
  recomendações de re-ingestão ou revisão manual.
- Se `$ARGUMENTS` contém `--fix`: pule a revisão **apenas** para findings
  `auto-fixável: sim` de nível aviso ou triviais de conformidade, conforme
  as "Regras de aplicação de fix" do catálogo. O restante ainda passa por
  aprovação.

Registre as aprovações no REPORT_FILE (seção `## Aprovados`).

## STEP 3 — Passe fix (subagente, só se houver aprovados)
Despache `brain-linter` de novo com `MODE: fix` e o mesmo REPORT_FILE. Ele
aplica exclusivamente os findings aprovados e registra a entrada `**Lint**:`
no `wiki/log.md`.

## STEP 4 — Fechamento
Resuma o resultado e apague o REPORT_FILE (o registro durável é o
`wiki/log.md`). Findings não aprovados: liste como pendências.

## Saída
```
pwdev-brain — LINT {{caminho}}

Findings    {{n}} ({{e}} erro · {{w}} aviso · {{i}} info)
Corrigidos  {{n}} · Pendentes {{n}} · Recomendações {{n}}

| Regra | Nível | Arquivo | Situação |
|---|---|---|---|
| BR-{{nnn}} | {{nível}} | {{arquivo}} | {{corrigido | pendente | recomendação}} |

Registro: wiki/log.md — entrada de {{YYYY-MM-DD}} {{gravada | — (nada corrigido)}}
```
