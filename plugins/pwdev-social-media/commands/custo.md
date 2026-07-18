---
description: Estima, confirma e acompanha o gasto com geradores pagos
argument-hint: "[campanha ou --estimar]"
---

# /pwdev-social-media:custo — Controle de custo

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Modo estimativa
Antes de um lote, rode a triagem de `cost-control` e apresente em **chamadas e
variações** — nunca em reais inventados. Preço unitário é do painel da ferramenta.

## Modo acompanhamento
Leia `.pwdev-social/gerados/manifest.jsonl` e reporte:

```
Campanha: {{nome}}
Chamadas: {{n}} · Ferramentas: {{quais}}
Ativos aprovados: {{n}} de {{n}} gerados
Taxa de aproveitamento: {{%}}
Rodadas médias por ativo: {{n}}
```

## Alertas
Levante quando:
- taxa de aproveitamento abaixo de **30%** → o problema é o prompt, não o modelo.
  A correção é `prompt-craft`, não mais orçamento
- mesmo ativo passou de **3 rodadas** → o caminho provavelmente não é geração
- vídeo gerado sem confirmação separada
- lote pedido sem seed fixada
- triagem mostrou que mais da metade não precisava ser gerada
