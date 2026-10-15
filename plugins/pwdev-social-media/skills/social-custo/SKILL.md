---
name: social-custo
description: >
  Use quando a pessoa perguntar quanto vai custar ou quanto gastou com geração —
  'quanto vai custar', 'orçamento', 'quanto gastei', 'controlar custo', 'está caro' — antes de
  qualquer lote e ao fechar campanha. Triagem do que não precisa ser gerado, estimativa pelo
  catálogo do pwdev-media, confirmação, orçamento mensal e acompanhamento pelo ledger. Não use para
  gerar (social-imagem) nem para escolher o modelo (media-catalogo do pwdev-media).
metadata:
  version: 3.0.0
---

# Controle de Custo

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma:
`<plugin-root>/references/language.md`.

Você protege o orçamento de quem paga a conta. Cada chamada tem preço.

## Princípio central

> **A geração mais barata é a que não acontece.** Antes de estimar custo, verifique se o ativo
> precisa mesmo ser gerado.

Boa parte do criativo de marca é tipografia sobre cor sólida ou sobre foto que já existe. Isso é
composição — Figma resolve na hora, de graça.

## Antes de qualquer lote

### 1. Triagem
Para cada ativo da tabela do conceito:

| Pergunta | Se sim |
|---|---|
| É texto sobre fundo liso? | **não gere** — Figma |
| Já existe foto no acervo? | **não gere** — use |
| Existe vetor no design system? | **não gere** — use |
| Dá para fotografar? | avalie: foto real costuma sair melhor e mais barata |
| É fundo, textura ou abstração? | gere |
| É cena que não existe e não dá para fotografar? | gere |

Reporte quantos ativos foram eliminados na triagem.

### 2. Estimativa

Para cada ativo a gerar, peça a estimativa ao núcleo (nada é cobrado):

```bash
pwdev-media gerar {{item}} --prompt '{{prompt}}' --n 2 [--duration 5] --estimar
```

O catálogo do `pwdev-media` traz o preço com **fonte e data de verificação**. Some e apresente:

```
Ativos a gerar:      4
Variações por ativo: 2 (primeira rodada)
Chamadas previstas:  8 · estimativa US$ {{total}} (preços de {{data}})
Rodadas de ajuste esperadas: 1-2

Vídeo:               1 clipe de 5s  ← item mais caro, confirmar separado
Upscale:             0
Orçamento do mês:    {{gasto}} de {{teto}} (pwdev-media custo orcamento)
```

Item sem preço no catálogo ("preço a verificar"): apresente em **chamadas** e diga que o provedor
informa o custo real depois. **Não invente valor.** Preço do catálogo velho (mais de 30 dias): sugira
`pwdev-media catalogo atualizar` antes de decidir.

### 3. Confirmação
Espere aprovação explícita do lote inteiro. Nunca gere "para mostrar como ficaria". O `--confirmar`
do `pwdev-media` é a segunda barreira — a barreira que importa é a conversa antes.

## Regra das 2 variações

Primeira rodada: **2 variações por ativo, sempre**. Não 8. Só gere volume depois que seed e modelo
estiverem fixados.

## Orçamento

```bash
pwdev-media custo orcamento            # mostra o teto mensal
pwdev-media custo orcamento 50         # define US$ 50/mês (só com o valor que a pessoa disse)
```

Uma geração que passaria do teto é bloqueada (código 4); só repita com `--acima-do-orcamento` com o
"sim" da pessoa.

## Acompanhamento

```bash
pwdev-media custo extrato [--mes AAAA-MM]
```

O ledger registra cada geração (item, custo, arquivos). Os arquivos da campanha ficam em
`.pwdev-social/gerados/<data>-<slug>/`: cruze os dois para fechar a campanha:

```
Campanha: {{nome}}
Chamadas: {{n}} · Itens: {{quais}} · Custo: US$ {{total}}
Ativos aprovados: {{n}} de {{n}} gerados
Taxa de aproveitamento: {{%}}
Rodadas médias por ativo: {{n}}
```

**Taxa de aproveitamento abaixo de 30% é sinal de prompt fraco**, não de modelo ruim. A correção é
`social-prompt`, não mais orçamento.

## Alertas

Levante a mão quando:

- o mesmo ativo passar de **3 rodadas** — o caminho provavelmente não é geração
- vídeo aparecer sem que alguém tenha confirmado o custo separadamente
- houver pedido de lote sem seed fixada
- a triagem mostrar que mais da metade dos ativos não precisava ser gerada

## Limites

- Não gera — ver `social-imagem`
- Não acessa o faturamento das plataformas: o custo real é o informado pelo provedor
- Não bloqueia gasto autorizado — informa, quem decide é a pessoa

## Skills relacionadas

- `social-prompt` — a maior alavanca de redução de custo
- `social-consistencia` — evita refação do conjunto
- `social-imagem`, `social-curadoria`, `social-lote`
