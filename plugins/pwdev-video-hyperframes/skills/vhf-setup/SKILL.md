---
name: vhf-setup
description: >
  Use quando a pessoa quiser preparar o computador para editar vídeo com HyperFrames ou conferir
  se está tudo pronto — 'configurar o editor de vídeo', 'instalar o hyperframes', 'status do
  editor', 'o render não funciona', 'falta o ffmpeg'. Confere e instala sem sudo o núcleo
  pwdev-media, ffmpeg, Node 22+ e as skills oficiais do HyperFrames, e desliga a telemetria. Não use
  para editar um vídeo (vhf-editar).
metadata:
  version: 0.2.0
---

# Preparar o editor de vídeo

Runtime: `<plugin-root>/references/runtime.md`. Tom: `<plugin-root>/references/language.md`.
Nunca use sudo. Diga quanto tempo cada passo leva antes de rodar.

## 1. Núcleo

```bash
pwdev-media versao
```

Faltou: carregue a skill `media-setup` do plugin pwdev-media (ou peça para instalar o plugin
`pwdev-media`) e volte aqui.

## 2. ffmpeg (30 s)

```bash
pwdev-media video ffmpeg || pwdev-media video ffmpeg --instalar
```

Fica em `~/.pwdev/bin`, sem senha. O `build.py` dos projetos já põe essa pasta no PATH do
HyperFrames.

## 3. Node 22+

```bash
node --version
```

Faltou ou é menor que 22: instale sem sudo pelo instalador oficial do Node para o usuário (macOS e
Linux: `fnm` ou `nvm`; Windows: o instalador `.msi` em modo usuário). Explique em uma frase e peça o
ok antes.

## 4. Skills oficiais do HyperFrames (1–2 min)

```bash
npx --yes hyperframes@0.8.158 skills update
npx --yes hyperframes@0.8.158 telemetry disable
```

Elas são usadas para escrever as cenas sob medida. Avise que só aparecem numa conversa nova.

## 5. Conferência

```bash
npx --yes hyperframes@0.8.158 doctor
pwdev-media status
```

Resuma em até 5 linhas: o que está pronto, o que falta e o próximo passo ("abra uma conversa nova e
peça: edita o vídeo da pasta X").

Pedido só de "status": rode o passo 5 e os testes dos passos 1–3 sem instalar nada.
