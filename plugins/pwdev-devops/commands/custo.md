---
description: Analisa custo AWS e identifica desperdício
argument-hint: "[período]"
---

# /pwdev-devops:custo

## STEP 0 — Idioma e conta
`${CLAUDE_PLUGIN_ROOT}/references/language.md` · `aws sts get-caller-identity`

## STEP 1 — Panorama
Custo do período, variação e top 5 serviços via Cost Explorer.

## STEP 2 — Os 8 desperdícios
Siga `finops`: NAT Gateway · EBS órfão · snapshot antigo · Elastic IP solto ·
recurso superdimensionado · S3 sem lifecycle · dev ligado 24/7 · log sem retenção.

## STEP 3 — Relatório
Tabela achado × economia estimada × esforço × risco.
**Só afirme economia com a conta à vista.** Sem base, `[VERIFICAR: preço unitário]`.

## STEP 4 — Antes de recomendar remoção
Todo "órfão" pode ter dono. Verifique tag, verifique se é dependência de DR,
pergunte de quem é.

Volume "não usado" que era o snapshot de DR é o erro caro deste domínio.

## STEP 5 — Entregar
Lista priorizada e os comandos. **Nada é removido pelo plugin.**
