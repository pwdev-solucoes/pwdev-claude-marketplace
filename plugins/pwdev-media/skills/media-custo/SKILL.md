---
name: media-custo
description: >
  Use quando a pessoa perguntar quanto gastou com geração de mídia por IA ou quiser controlar o
  gasto — 'quanto gastei este mês', 'extrato de custos', 'definir orçamento de 30 dólares', 'tirar
  o limite', 'o que mais custou'. Lê o ledger local do pwdev-media e define o teto mensal. Não use
  para estimar uma geração específica (media-gerar faz isso antes de gerar).
metadata:
  version: 0.3.0
---

# Custo e orçamento

Runtime e CLI: `<plugin-root>/references/runtime.md`.

```bash
pwdev-media custo extrato [--mes AAAA-MM]
pwdev-media custo orcamento            # mostra o teto
pwdev-media custo orcamento 30         # define US$ 30/mês
pwdev-media custo orcamento -1         # remove o teto
```

O extrato usa o custo informado pelo provedor e, quando ele não informa, a estimativa do
catálogo; diga isso quando houver estimativas no total. Resuma em até 5 linhas: total do mês,
teto, os 3 itens que mais custaram e quanto foi reaproveitado do cache.

Mudar o teto é uma decisão da pessoa: só rode `orcamento <valor>` com o valor que ela disse.
