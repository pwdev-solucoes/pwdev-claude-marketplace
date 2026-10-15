---
name: media-formatos
description: >
  Use quando a pessoa ou outro plugin precisar do tamanho e da zona segura de um formato de
  criativo — 'qual o tamanho do Reels', 'formatos para anúncio no Google', 'esse texto cabe na
  zona segura do TikTok?', 'quais formatos do Meta', 'tamanho do banner 300x250'. Lista formatos
  por plataforma, mostra a zona segura em pixels e confere se um elemento está dentro. Não use
  para gerar o criativo (media-gerar ou pwdev-social-media).
metadata:
  version: 0.5.0
---

# Formatos e zonas seguras

Runtime e CLI: `<plugin-root>/references/runtime.md`.

```bash
pwdev-media formatos listar [--plataforma instagram|facebook|tiktok|youtube|linkedin|google|pinterest]
pwdev-media formatos mostrar reels-9x16
pwdev-media formatos conferir reels-9x16 --caixa 120,300,840,180   # x,y,largura,altura em px
```

`conferir` sai com código 0 quando o elemento está dentro e 1 com o lado e os pixels que sobram.

As margens vêm de guias públicos das plataformas e mudam com o tempo: ao entregar, diga
"conferir na rede de destino" e a data de `verificado_em`. Para um criativo em vários formatos,
liste os ids escolhidos e a zona segura de cada um antes de compor.
