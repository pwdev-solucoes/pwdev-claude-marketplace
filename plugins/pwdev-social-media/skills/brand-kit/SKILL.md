---
name: brand-kit
description: >
  Extrai o brand kit do Figma — tokens de cor, tipografia, grid, logo e
  componentes — e grava na seção 3 do contexto. Use quando o usuário disser
  "extrair a marca", "pegar os tokens", "quais as cores", "design system",
  "importar do Figma", "montar brand kit", ou quando a seção 3 estiver vazia.
  Lê do Figma; não inventa paleta.
metadata:
  version: 1.0.0
---

# Brand Kit

Você é design systems engineer. Extrai a verdade do arquivo, não da memória.

## Princípio central

> Token tem nome. Hex não. Um criativo montado com `#0A5C36` quebra quando a
> marca muda; montado com `color/brand/primary`, acompanha.

## Antes de começar

Leia a seção 2 do contexto para pegar a URL do design system.

### Path A — Figma conectado

**Portão obrigatório:** carregue `/figma-use` antes de qualquer `use_figma`.

```
1. get_design_context(URL do DS)
2. get_variable_defs()          ← a fonte real dos tokens
3. search_design_system()       ← componentes existentes
4. get_libraries()              ← o que está publicado
5. get_screenshot()             ← conferência visual
```

Extraia:

| O que | De onde | Grave como |
|---|---|---|
| Cores | variáveis de cor | nome do token + valor + uso |
| Tipografia | estilos de texto | família, pesos, escala |
| Espaçamento | variáveis numéricas | escala |
| Grid | layout grids dos frames | margem, colunas, gutter |
| Logo | componente ou nó de logo | caminho + área de proteção |
| Componentes | biblioteca publicada | nome + para que serve |

### Path B — Sem Figma
Peça o manual de marca ou 3-5 peças aprovadas. Extraia o que der e **marque
cada item como inferido**, não como oficial. Diga que o brand kit é provisório
até alguém confirmar contra o arquivo real.

Nunca invente paleta a partir de "a marca é verde".

## Auditoria

Ao extrair, aponte o que estiver quebrado — é o momento em que isso aparece:

- cor usada em peça que **não** é token (valor solto)
- token duplicado com nomes diferentes
- estilo de texto fora da escala
- componente com cinco variantes que deveriam ser um
- contraste insuficiente entre pares de token usados juntos

Reporte como achados, não conserte sozinho — o arquivo é do time de design.

## Formato de saída

Atualize a **seção 3** do contexto e apresente:

```markdown
## Brand kit — {{organização}}
Origem: {{URL}} | Extraído em: {{data}} | Confiança: oficial | inferido

### Cores
| Token | Valor | Uso | Contraste sobre fundo padrão |

### Tipografia
### Grid
### Componentes reaproveitáveis
### Achados
| Problema | Onde | Severidade |
```

A coluna de contraste é obrigatória — é o que `creative-review` vai cobrar depois.

## Limites

- Não altera o arquivo do Figma — extrai e reporta
- Não cria design system — ver `/figma-generate-library`
- Não monta peça — ver as skills de montagem
- Não inventa token ausente

## Skills relacionadas

- `social-context` — consome a extração
- `creative-review` — usa os contrastes registrados aqui
- `figma-pipeline` (referência) — o fluxo de leitura
