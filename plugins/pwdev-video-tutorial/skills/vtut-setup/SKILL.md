---
name: vtut-setup
description: >
  Use quando a pessoa quiser preparar o computador para criar vídeos tutoriais e explicativos de
  sistemas, ou conferir se está tudo pronto — 'configurar o tutorial de sistema', 'instalar o
  gravador de tela', 'status do pwdev-video-tutorial', 'a narração não funciona'. Confere e instala
  sem sudo playwright-cli, núcleo pwdev-media, ffmpeg, Node, a voz local em português (Kokoro) e o
  pwdev-video-hyperframes para a montagem. Não use para explorar um sistema (vtut-explorar) nem
  para gravar (vtut-gravar).
metadata:
  version: 0.1.0
---

# Preparar o estúdio de tutoriais

Runtime: `<plugin-root>/references/runtime.md`. Tom: `<plugin-root>/references/language.md`.
Nunca use sudo. Diga quanto tempo cada passo leva.

## 1. Ferramentas

```bash
playwright-cli --version || npm install -g @playwright/cli@latest     # ~1 min
pwdev-media versao
pwdev-media video ffmpeg || pwdev-media video ffmpeg --instalar
node --version                                                         # 22 ou mais
```

Sem `pwdev-media`: skill `media-setup` do plugin pwdev-media. Sem `npm` global gravável: use
`npx playwright-cli` em todos os comandos. A montagem usa o `pwdev-video-hyperframes`: confira se o
plugin está instalado (skill `vhf-setup`).

## 2. Voz local em português (grátis, ~2 min, uma vez)

```bash
uv venv --python 3.12 ~/.pwdev/venvs/tts
uv pip install --python ~/.pwdev/venvs/tts/bin/python kokoro-onnx soundfile
```

O primeiro uso baixa o modelo Kokoro (~300 MB). Vozes pt-BR: `pf_dora` (feminina), `pm_alex` e
`pm_santa` (masculinas). Para voz mais natural, a ElevenLabs entra pelo pwdev-media (paga, com
estimativa e "sim"); ou a pessoa grava a própria voz.

## 3. Conferência

```bash
playwright-cli open about:blank && playwright-cli close
pwdev-media status
```

Resuma em até 5 linhas o que está pronto e o próximo passo: "me diga o endereço do sistema (de
preferência homologação) e, se puder, a pasta do código".

Pedido só de "status": rode as verificações sem instalar nada.
