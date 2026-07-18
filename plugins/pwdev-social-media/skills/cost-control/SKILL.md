---
name: cost-control
description: >
  Estima, confirma e acompanha o gasto com geradores pagos. Use quando o usuário
  disser "quanto vai custar", "orçamento", "quanto gastei", "controlar custo",
  "está caro", antes de qualquer lote de geração, ou ao fechar campanha.
  Com APIs no centro, custo deixa de ser detalhe e vira restrição de projeto.
metadata:
  version: 1.0.0
---

# Controle de Custo

Você protege o orçamento de quem paga a conta. Cada chamada tem preço.

## Princípio central

> **A geração mais barata é a que não acontece.** Antes de estimar custo,
> verifique se o ativo precisa mesmo ser gerado.

Boa parte do criativo de marca é tipografia sobre cor sólida ou sobre foto que
já existe. Isso é composição — Figma resolve na hora, de graça.

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

Reporte quantos ativos foram eliminados na triagem. É o número que mais
impressiona e o mais fácil de conseguir.

### 2. Estimativa

Apresente em **chamadas e variações**, nunca em reais inventados:

```
Ativos a gerar:     4
Variações por ativo: 2 (primeira rodada)
Chamadas previstas:  8
Rodadas de ajuste esperadas: 1-2
Total provável:      12-16 chamadas

Vídeo:               1 clipe de 5s  ← item mais caro, por larga margem
Upscale:             0

Ferramenta: {{qual}} · Consulte o preço unitário no painel
```

**Não invente preço em reais.** Preço muda e número errado aqui vira decisão
errada lá. Entregue a contagem; o preço unitário é do painel da ferramenta.

### 3. Confirmação
Espere aprovação explícita. Nunca gere "para mostrar como ficaria".
Nunca gere lote sem autorização do lote inteiro.

Os scripts exigem `--confirm` como segunda barreira — mas a barreira que importa
é a conversa antes.

## Regra das 2 variações

Primeira rodada: **2 variações por ativo, sempre**. Não 8.

Com 2 você já diagnostica se o prompt está na direção certa. Gerar 8 de um
prompt errado é pagar oito vezes pelo mesmo erro.

Só gere volume depois que seed e modelo estiverem fixados.

## Acompanhamento

O manifesto (`.pwdev-social/gerados/manifest.jsonl`) registra tudo. Ao fechar
campanha, reporte:

```
Campanha: {{nome}}
Chamadas: {{n}} · Ferramentas: {{quais}}
Ativos aprovados: {{n}} de {{n}} gerados
Taxa de aproveitamento: {{%}}
Rodadas médias por ativo: {{n}}
```

**Taxa de aproveitamento abaixo de 30% é sinal de prompt fraco**, não de modelo
ruim. Aponte isso — a correção é `prompt-craft`, não mais orçamento.

## Alertas

Levante a mão quando:

- o mesmo ativo passar de **3 rodadas** — o caminho provavelmente não é geração
- vídeo aparecer sem que alguém tenha confirmado o custo separadamente
- houver pedido de lote sem seed fixada
- a triagem mostrar que mais da metade dos ativos não precisava ser gerada

## Limites

- Não gera — ver `image-gen`
- Não informa preço unitário: consulte o painel da ferramenta
- Não bloqueia gasto autorizado — informa, quem decide é o usuário
- Não acessa faturamento das plataformas

## Skills relacionadas

- `prompt-craft` — a maior alavanca de redução de custo
- `visual-consistency` — evita refação do conjunto
- `image-gen`, `asset-curation`
