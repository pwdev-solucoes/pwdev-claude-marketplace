---
name: vtut-montar
description: >
  Use quando for transformar a gravação de tela e a narração no vídeo final do tutorial — 'monta o
  vídeo do tutorial', 'põe legenda e zoom', 'versão vertical do tutorial', 'gera o vídeo final do
  passo a passo'. Junta gravação e narração na pasta de edição, cria legendas em faixa legível,
  zoom no elemento clicado e o projeto HyperFrames, e gera também o tutorial em texto com capturas.
  Não use para gravar (vtut-gravar) nem para editar vídeo falado de câmera (pwdev-video-hyperframes).
metadata:
  version: 0.1.0
---

# Montagem

Runtime e pastas: `<plugin-root>/references/runtime.md`. A composição e o render são do plugin
`pwdev-video-hyperframes` (skills `vhf-*`); este passo prepara tudo para ele.

## 1. Pasta de edição

```bash
python3 '<plugin-root>/scripts/tutorial.py' montar '<V>' --edit '<V>/edit' --roteiro '<V>/roteiro.json' [--formato youtube-16x9]
```

- `cut.mp4` = gravação + narração de cada cena no seu início, volume normalizado;
- legendas: pela transcrição da narração (tempo exato por palavra); sem o modelo de transcrição,
  pelo texto do roteiro distribuído na fala (`origem_palavras: texto` — avise que é aproximado);
- `<V>/sugestoes-projeto.json`: zoom 1,25 no elemento de cada clique e legenda `caixa` (faixa
  escura, legível sobre interface clara), embaixo e com até 6 palavras.

Formato vertical (`reels-9x16`) para novidade em rede social: grave o roteiro com `viewport`
1080×1920 (versão mobile do sistema) em vez de recortar um vídeo largo.

## 2. Projeto HyperFrames

Crie o projeto com o comando `novo` do passo "Projeto" da skill `vhf-editar` (é ela que sabe onde o
pwdev-video-hyperframes está instalado neste runtime), com estes valores:

- destino `'<V>/projeto-hf'`, `--edit '<V>/edit'`, `--formato youtube-16x9`, `--nome <video-id>`.

Depois desse comando, o projeto é autossuficiente: tudo roda pelo `'<V>/projeto-hf/build.py'`.

Copie `blocos` e `legenda` de `sugestoes-projeto.json` para `<V>/projeto-hf/projeto.json`. Se a
legenda mudou para 6 palavras, refaça: `pwdev-media video legendas '<V>/edit' --max-palavras 6`.
Título do capítulo já está na gravação; `textos` extras só se ajudarem (uma ideia por vez).

```bash
python3 '<V>/projeto-hf/build.py' amostra 0 12
python3 '<V>/projeto-hf/build.py' estudio
```

## 3. Tutorial em texto

```bash
python3 '<plugin-root>/scripts/tutorial.py' texto '<V>' --roteiro '<V>/roteiro.json'
```

Gera `<V>/tutorial.md` (passos numerados com as capturas), pronto para a central de ajuda ou um site
de documentação. Próximo: `vtut-revisar`.
