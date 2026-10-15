---
name: vrm-setup
description: >
  Use quando a pessoa quiser preparar o computador para editar vídeo com Remotion ou conferir se
  está tudo pronto — 'configurar o remotion', 'instalar o editor em React', 'status do editor
  remotion', 'o render do remotion falha', 'preciso de licença do remotion?'. Confere e instala sem
  sudo o núcleo pwdev-media, ffmpeg, Node 20+ e as skills oficiais do Remotion, e explica a licença.
  Não use para editar um vídeo (vrm-editar).
metadata:
  version: 0.2.0
---

# Preparar o editor de vídeo com Remotion

Runtime: `<plugin-root>/references/runtime.md`. Tom: `<plugin-root>/references/language.md`.
Nunca use sudo. Diga quanto tempo cada passo leva antes de rodar.

## 1. Licença (primeiro, uma vez)

Leia `<plugin-root>/references/licenca.md` e diga em uma frase: o Remotion é grátis para pessoa
física e empresa de até 3 pessoas; acima disso, a empresa precisa da Company License. Se a pessoa não
souber ou a empresa for maior, recomende o `pwdev-video-hyperframes` (Apache-2.0, mesmo fluxo e mesmo
`projeto.json`) e só siga com o "sim" dela.

## 2. Núcleo e ffmpeg

```bash
pwdev-media versao
pwdev-media video ffmpeg || pwdev-media video ffmpeg --instalar
```

Faltou o núcleo: skill `media-setup` do plugin pwdev-media. O ffmpeg é usado pelo corte; o render do
Remotion traz o próprio.

## 3. Node 20+

```bash
node --version
```

Faltou ou é antigo: instale sem sudo pelo gerenciador de versões do usuário (macOS/Linux: `fnm` ou
`nvm`; Windows: instalador `.msi` em modo usuário). Explique e peça o ok antes.

## 4. Skills oficiais do Remotion (1 min)

```bash
npx --yes skills add remotion-dev/skills
```

São usadas para escrever cenas sob medida em React. Só aparecem numa conversa nova.

## 5. Primeiro render baixa o navegador

O primeiro `checar` ou `render` de um projeto baixa o Chrome Headless Shell (~170 MB) uma vez. Avise.

## 6. Conferência

```bash
pwdev-media status
```

Resuma em até 5 linhas: o que está pronto, o que falta e o próximo passo ("abra uma conversa nova e
peça: edita o vídeo da pasta X em Remotion").

Pedido só de "status": rode os testes dos passos 2–3 e o 6, sem instalar nada.
