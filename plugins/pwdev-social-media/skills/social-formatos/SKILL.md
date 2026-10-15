---
name: social-formatos
description: >
  Use quando a pessoa perguntar tamanho, proporção, zona segura ou tipografia mínima,
  ou quiser o mesmo criativo em vários formatos — 'qual o tamanho do Reels', 'área segura', 'cabe
  texto onde', 'adapta para 4:5, 1:1 e 16:9', 'versões para display do Google'. Usa os formatos do
  pwdev-media, confere caixas de texto na zona segura e deriva uma peça em todos os formatos.
  Não use para conceber a peça (social-conceito).
metadata:
  version: 3.0.0
---

# Formatos e derivação multiformato

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma:
`<plugin-root>/references/language.md`. Tipografia mínima, slides e contraste:
`<plugin-root>/references/formatos.md`.

## Princípio central

> Dimensão e zona segura vivem em **um** lugar: o catálogo de formatos do `pwdev-media`. Skill que
> decora número fica errada na próxima atualização de plataforma.

## Consultar

```bash
pwdev-media formatos listar [--plataforma instagram|facebook|tiktok|youtube|linkedin|google|pinterest]
pwdev-media formatos mostrar reels-9x16                          # dimensão e zona segura em px
pwdev-media formatos conferir feed-4x5 --caixa 64,120,952,300     # x,y,largura,altura em px
```

`conferir` sai com código 0 quando a caixa está dentro e 1 com o lado e os pixels que sobram. Responda
sempre com:

1. dimensão em pixels e proporção
2. zona segura em pixels
3. tipografia mínima (`<plugin-root>/references/formatos.md`)
4. o alerta de validade

> Zonas seguras mudam a cada atualização de app. As margens do catálogo são conservadoras e têm data
> de verificação; antes de campanha grande, confira na rede de destino.

## Escolha de formato

| Objetivo | Formato (`id`) |
|---|---|
| Máxima superfície no feed | `feed-4x5` — 1080 × 1350 |
| Conteúdo educativo em sequência | carrossel em `feed-4x5` |
| Alcance por vídeo curto | `reels-9x16`, `tiktok-9x16`, `shorts-9x16` |
| Link com prévia | `link-1.91x1` — 1200 × 628 |
| Tutorial, YouTube | `youtube-16x9` |
| Busca (Pinterest) | `pinterest-2x3` |
| Mídia paga no Google | `display-300x250`, `display-336x280`, `display-728x90`, `display-970x250`, `display-160x600`, `display-320x50` |

## Derivar um criativo em vários formatos

Quando a pessoa aprova uma peça e pede "todos os formatos" (ou a campanha exige):

1. **Escolher os ids** — padrão para social: `reels-9x16`, `feed-4x5`, `feed-1x1`, `youtube-16x9`,
   `link-1.91x1`; mídia paga acrescenta os `display-*`. Liste e confirme.
2. **Mapa de adaptação** — para cada formato, decida o que muda (não estique):

   | Formato | Hierarquia | Ajuste típico |
   |---|---|---|
   | 9:16 | 1º e CTA dentro da zona segura alta | empilhar; o app cobre topo e base |
   | 4:5 / 1:1 | os três níveis | margem de 64 px; 1:1 corta o 2º nível se faltar altura |
   | 16:9 / 1,91:1 | 1º nível à esquerda, visual à direita | layout horizontal |
   | display pequeno (320×50, 728×90) | só o 1º nível + marca + CTA | sem texto de apoio |

3. **Conferir cada caixa de texto** com `pwdev-media formatos conferir <id> --caixa x,y,l,a`. Caixa fora:
   reposicione antes de montar.
4. **Ativo gerado** que não cabe numa proporção: gere uma variação nova com o mesmo prompt e seed na
   proporção do formato (`social-imagem`, com estimativa) em vez de cortar o rosto ou o produto.
5. **Montar** com `social-figma` (componente com uma variante por formato) ou entregar a
   especificação por formato.
6. **Revisar** cada formato com `social-revisao` e entregar com `social-entrega` (nome do arquivo leva
   o formato).

## Saída

```
Peça base: {{nome}} — {{formato base}}
| Formato | Dimensão | Zona segura | Caixas conferidas | Ajuste |
Pendências: {{lista}}
```

## Limites

- Não monta peça — ver `social-figma` e as skills de montagem
- Não escreve copy nem define conteúdo
- Não garante a zona segura além da data de verificação do catálogo

## Skills relacionadas

- Todas as skills de montagem consomem esta
- `social-revisao` — valida a peça contra estas medidas
- `social-lote` — matriz de versões em vários formatos
