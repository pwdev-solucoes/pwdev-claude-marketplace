---
name: social-lote
description: >
  Use quando a pessoa quiser muitas versões de um criativo para testar — 'lote de criativos',
  'versões para teste A/B', 'vários ganchos', 'matriz de criativos', 'gera 12 variações para
  anúncio', 'todas as combinações de gancho e formato'. Monta a matriz gancho × visual × formato,
  estima o custo do lote inteiro antes de qualquer "sim", produz e registra tudo numa planilha de
  versões. Não use para uma peça só (social-criar) nem para adaptar uma peça aprovada a formatos
  (social-formatos).
metadata:
  version: 3.0.0
---

# Lote de criativos (matriz de versões)

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma:
`<plugin-root>/references/language.md`.

## Princípio central

> Lote é teste, não volume. **Cada versão muda uma coisa só** — senão o resultado não diz o que
> funcionou.

## 1. Montar a matriz

Três eixos, cada um com poucas opções:

| Eixo | De onde vem | Típico |
|---|---|---|
| **Gancho** (texto da peça) | copy aprovada do `pwdev-copy` — nunca inventado aqui | 2–4 |
| **Visual** (ativo) | ativos aprovados na curadoria, ou a gerar | 1–3 |
| **Formato** | ids de `pwdev-media formatos listar` | 1–3 |

Combinações = ganchos × visuais × formatos. Acima de **12**, proponha cortar: teste primeiro gancho ×
visual em um formato e só depois derive os vencedores para os outros formatos (`social-formatos`).

## 2. Custo do lote inteiro, antes de tudo

Some só o que precisa ser **gerado** (o texto do gancho é composição e não custa geração):

```bash
pwdev-media gerar {{item}} --prompt '{{prompt}}' --n 2 --estimar     # por visual a gerar
```

```
Versões no lote:        {{n}}  (ganchos {{a}} × visuais {{b}} × formatos {{c}})
Visuais a gerar:        {{n}} · chamadas {{n}} · estimativa US$ {{total}}
Composição (sem custo): {{n}} peças
Orçamento do mês:       {{gasto}} de {{teto}}
```

**Um único "sim" para o lote inteiro**, com o total na frente. Nunca vá pedindo de pouco em pouco.

## 3. Produzir

1. Visuais: `social-imagem` (2 variações, curadoria, seed registrada). Reaproveite a mesma seed entre
   formatos para manter a consistência.
2. Peças: componente com uma variante por gancho e por formato (`social-figma`), ou especificação por
   versão.
3. Cada versão passa em `social-revisao` e ganha alt text (`social-alt-text`).

## 4. Planilha de versões

Grave `.pwdev-social/lotes/{{AAAA-MM-DD}}-{{campanha}}.csv`:

```
versao,gancho,visual,seed,formato,arquivo,revisao,alt_text
v01,"{{gancho A}}",fundo-1,{{seed}},feed-4x5,{{arquivo}},APROVADO,sim
```

O nome do arquivo de cada peça leva a versão (`social-entrega`). É a planilha que o time de mídia usa
para ler o resultado do teste depois — sem ela, o teste não ensina nada.

## 5. Entregar

Resumo em até 6 linhas: versões produzidas, aprovadas, custo real (`pwdev-media custo extrato`) e onde
está a planilha. **Não publica nem sobe campanha.**

## Limites

- Não escreve ganchos — ver `pwdev-copy`
- Não decide o vencedor do teste — isso vem dos dados de mídia
- Não gera sem o "sim" do lote inteiro

## Skills relacionadas

- `social-custo`, `social-imagem`, `social-formatos`, `social-revisao`, `social-entrega`
