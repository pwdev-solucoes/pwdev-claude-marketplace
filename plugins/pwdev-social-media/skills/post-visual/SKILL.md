---
name: post-visual
description: >
  Monta peça única de feed — quote card, card de dado, capa, anúncio estático,
  imagem de link. Use quando o usuário disser "post", "card", "peça do feed",
  "imagem do post", "arte para o LinkedIn", "criativo estático", "quote card",
  "card de dado". Para sequência ver carousel-builder; para vertical ver
  story-reels.
metadata:
  version: 1.0.0
---

# Peça de Feed

Você monta a peça que precisa funcionar em uma olhada, no meio de uma rolagem.

## Princípio central

> A peça compete com o polegar, não com outras peças. **Dois segundos** é todo
> o tempo que existe.

## Antes de montar
Copy aprovada · conceito · brand kit · formato. Faltando qualquer um, pare e
aponte a skill que resolve.

## Tipos

| Tipo | Quando | Mecanismo |
|---|---|---|
| **Quote card** | frase forte carrega sozinha | tipografia dominante |
| **Card de dado** | o argumento é o número | número gigante + contexto mínimo |
| **Capa de artigo** | levar para conteúdo longo | título + marca |
| **Demonstração** | mostrar o produto | screenshot com destaque |
| **Anúncio estático** | tráfego pago | promessa + CTA visível |
| **Institucional** | comunicado, serviço público | identidade + informação clara |

## Hierarquia

Três níveis, nunca mais:

```
1º   a ideia          72-120 px    lê em 1 segundo
2º   o suporte        36-48 px     lê em 3 segundos
3º   fonte, CTA, logo 24-28 px     lê se parar
```

Se tudo tem o mesmo peso, nada tem peso. O erro mais comum é o nível 3 competir
com o nível 1 — logo grande demais, CTA gritando.

## Card de dado

O número é o elemento visual, não um texto grande.

```
1º   o número                    120-200 px
2º   o que ele significa         36-44 px
3º   fonte e data                24 px    ← obrigatório
```

**Sem fonte visível, o card não sai.** Número sem procedência em peça pública é
falha grave — em setor público, é risco institucional. Sem fonte, use
`[PREENCHER: fonte do dado]` e não aprove.

## Montagem

**Portão:** `/figma-use` antes de `use_figma`.

1. `get_variable_defs` + `search_design_system`
2. Reaproveitar componente de card, se existir
3. Montar em Auto Layout — o texto muda de tamanho, o layout precisa acompanhar
4. Nomear `{{campanha}}/{{formato}}/{{n}}`
5. `get_screenshot`

**Formato padrão: 4:5 (1080 × 1350).** Só use 1:1 quando o time pedir — 4:5
ocupa mais altura de tela e rende mais alcance no feed.

## Texto sobre foto

Nunca confie no contraste direto. Aplique sobreposição sólida, gradiente ou
caixa. Meça o contraste contra a **região mais clara sob o texto** — não contra
a média da imagem. Ver `acessibilidade.md`.

## Anti-padrões

- Logo maior que a mensagem
- Texto sobre foto sem sobreposição
- Dado sem fonte
- Três mensagens na mesma peça
- Fonte abaixo de 24 px
- Foto de banco genérica
- CTA em peça orgânica que não leva a lugar nenhum

## Limites

- Não escreve copy — ver `pwdev-copy`
- Não define conceito — ver `creative-concept`
- Não gera foto ou ilustração — ver `image-gen`
- Não aprova nem exporta

## Skills relacionadas

- `creative-concept`, `figma-pipeline`, `creative-review`, `alt-text`
