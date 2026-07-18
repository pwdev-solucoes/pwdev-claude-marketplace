---
name: carousel-builder
description: >
  Monta carrossel completo — estrutura de slides, hierarquia por slide e
  construção no Figma como componente com variantes. Use quando o usuário disser
  "carrossel", "slides", "carrossel do LinkedIn", "carrossel do Instagram",
  "post em sequência", "documento do LinkedIn". Recebe a copy slide a slide e
  entrega frames montados e revisados.
metadata:
  version: 1.0.0
  derivado-de: >
    carousel-writer-sms (social-media-skills, MIT, © 2026 Social Media Skills
    Contributors) — que produz texto; esta produz a peça
---

# Carrossel

Você monta o formato de maior retenção do feed. Cada slide precisa ganhar o
próximo swipe.

## Princípio central

> O slide 1 é o único que todo mundo vê. **Se ele não funciona sozinho, os
> outros nove não existem.**

## Antes de montar

| Insumo | Se faltar |
|---|---|
| Copy slide a slide | `/pwdev-copy:copy social` |
| Conceito visual | `creative-concept` |
| Brand kit | `brand-kit` |
| Plataforma e contagem | perguntar |

## Estrutura

```
Slide 1     capa — o gancho, sozinho, legível em miniatura
Slide 2     o problema ou a promessa; a ponte entre gancho e valor
Slide 3..n-1  um ponto por slide — inegociável
Slide n     recapitulação + CTA
```

| Plataforma | Mínimo | Ideal | Formato |
|---|---|---|---|
| Instagram | 5 | 8-10 | 1080 × 1350 |
| LinkedIn | 5 | 7-12 | PDF 1080 × 1350 |
| Facebook | 3 | 5-8 | 1080 × 1350 |

Abaixo de 5 slides não justifica o formato — vira post único.

## Limites por slide

- Título: **até 8 palavras**
- Corpo: **até 30 palavras**
- Uma ideia por slide

Passou disso, são dois slides. Não reduza o corpo de fonte para caber — reduzir
fonte para caber texto é o erro que mais destrói legibilidade em carrossel.

## Montagem no Figma

**Portão:** `/figma-use` antes de `use_figma`.

Ordem:

1. `get_variable_defs` — tokens
2. `search_design_system` — já existe componente de slide?
3. Criar **um componente** `Slide` com variantes:
   `capa` · `conteúdo` · `dado` · `contraste` · `fechamento`
4. Instanciar por slide, preenchendo o texto
5. Nomear `{{campanha}}/carrossel/{{n}}`
6. `get_screenshot` de cada frame

> **Não crie dez frames soltos.** Slide é componente com variantes — do
> contrário, mudar a margem exige editar dez peças à mão.

### Progressão visual
O leitor precisa saber onde está. Escolha um sinal e mantenha:
indicador numérico, barra de progresso ou variação cromática progressiva.

### Borda
Reserve **80 px na borda externa** — o gesto de swipe e o indicador de página
ocupam essa faixa. Ver `format-specs`.

## Path B — Sem Figma

Entregue a especificação slide a slide: dimensão, grid, hierarquia, token por
elemento, corpo de fonte, conteúdo exato. Declare que não montou.

## Depois

Rode `creative-review` e `alt-text`. Carrossel exige texto alternativo
**por slide** — é o formato que mais falha em acessibilidade.

## Anti-padrões

- Dez frames soltos em vez de componente com variantes
- Reduzir fonte para caber texto
- Slide de capa que só faz sentido depois de ler o slide 2
- Último slide sem CTA
- Texto na faixa de 80 px da borda
- Contagem ímpar sem motivo — quebra a paginação visual em algumas grades

## Limites

- Não escreve a copy dos slides — ver `pwdev-copy`
- Não define conceito — ver `creative-concept`
- Não exporta PDF — ver `export-handoff`
- Não publica

## Skills relacionadas

- `creative-concept`, `figma-pipeline`, `creative-review`, `alt-text`, `format-specs`
