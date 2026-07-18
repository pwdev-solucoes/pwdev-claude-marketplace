---
name: story-reels
description: >
  Monta peças verticais 9:16 — story, reels, shorts, TikTok — respeitando as
  áreas seguras da interface. Use quando o usuário disser "story", "reels",
  "shorts", "vertical", "9:16", "TikTok", "capa de reels", "template de story".
  A restrição dominante aqui é a UI do app, que cobre topo, base e lateral.
metadata:
  version: 1.0.0
---

# Vertical 9:16

Você monta no formato onde o app **come parte da tela**. Ignorar isso é o erro
que mais gera republicação.

## Princípio central

> A tela tem 1080 × 1920. A área utilizável tem cerca de **900 × 1350**.
> Projetar para 1920 de altura é projetar para ser coberto.

## Áreas seguras

Base 1080 × 1920:

```
topo         250 px   perfil, som, indicador de sequência
base         320 px   legenda, CTA, barra de progresso
direita      120 px   curtir, comentar, compartilhar
esquerda      60 px   margem visual
```

Área confiável: **900 × 1350 centralizada, deslocada para cima.**

> Erro mais comum: chamada no rodapé, onde a legenda do app cobre.
> Segundo mais comum: elemento à direita, atrás dos botões de ação.

**Ressalva de validade:** áreas seguras mudam a cada atualização de app. Os
valores acima são conservadores. Confirme antes de campanha grande e atualize
`references/formatos.md`.

## Estrutura

```
0-1s     gancho — precisa funcionar mudo e sem contexto
1-3s     desenvolvimento
3s-fim   entrega
final    CTA dentro da área segura
```

Story em sequência: cada card precisa sobreviver sozinho. As pessoas entram no
meio da sequência o tempo todo.

## Vídeo

- **Legenda embutida é obrigatória.** A maioria assiste sem som — e sem legenda
  a peça é inacessível para pessoa surda. Não é preferência, é acessibilidade.
- Legenda dentro da área segura, nunca no rodapé
- Sem piscar acima de 3 Hz — risco de convulsão fotossensível
- Texto na tela: mínimo 32 px, alto contraste, tempo de leitura suficiente

## Montagem

**Portão:** `/figma-use` antes de `use_figma`.

1. Criar frame 1080 × 1920
2. **Criar guias da área segura como primeira ação** — antes de qualquer conteúdo
3. Montar o conteúdo inteiro dentro de 900 × 1350
4. Conferir com `get_screenshot` que nada crítico saiu da área
5. Nomear `{{campanha}}/9x16/{{n}}`

Faça um componente `Story base` com as guias — assim toda peça nasce correta.

## Anti-padrões

- CTA no rodapé
- Elemento importante na faixa direita
- Texto colado na borda superior
- Vídeo sem legenda
- Reaproveitar peça 4:5 esticada para 9:16
- Texto pequeno "porque é vertical" — a distância de leitura é a mesma

## Limites

- Não edita nem gera vídeo — ver `video-gen`
- Não escreve copy — ver `pwdev-copy`
- Não publica
- Não garante área segura além da data de atualização de `formatos.md`

## Skills relacionadas

- `creative-concept`, `figma-pipeline`, `creative-review`, `video-gen`, `format-specs`
