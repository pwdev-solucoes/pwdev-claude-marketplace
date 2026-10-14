---
name: media-setup
description: >
  Use quando a pessoa quiser instalar, configurar ou conferir o pwdev-media — 'configurar o
  pwdev-media', 'instalar a suíte de mídia', 'guardar minha chave do OpenRouter', 'a chave da
  ElevenLabs está funcionando?', 'status do pwdev-media'. Instala a CLI, confere ffmpeg/Node,
  guarda chaves no Keychain sem passar pelo chat, testa cada provedor ao vivo e mostra idade do
  catálogo e gasto do mês. Não use para gerar mídia (media-gerar), escolher modelo
  (media-catalogo) ou atualizar o catálogo (media-atualizar).
metadata:
  version: 0.2.0
---

# Instalar e conferir o pwdev-media

Ferramentas por runtime e segredos: `<plugin-root>/references/runtime.md`. Idioma:
`<plugin-root>/references/language.md`. Fale em frases curtas; nunca cole comando longo, log ou
chave na conversa.

## 1. CLI

```bash
pwdev-media versao || uv tool install --force <plugin-root>/engine
```

Sem `uv`: instale sem sudo (macOS/Linux `curl -LsSf https://astral.sh/uv/install.sh | sh`; Windows
`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`) e use o
caminho completo `~/.local/bin/uv` até abrir um terminal novo. Nunca use sudo.

## 2. Estado

```bash
pwdev-media status
```

Mostre em até 6 linhas: ferramentas que faltam, chaves configuradas, idade do catálogo e gasto do
mês. Pedido de "status" sem mais nada: rode também `pwdev-media status --ao-vivo` (chamadas
gratuitas) e pare aqui.

`ffmpeg` ou `node` faltando só importa para os plugins de vídeo: avise e diga que o
`pwdev-video-hyperframes` ou o `pwdev-video-remotion` instala na hora certa.

## 3. Chaves

Recomende começar pelo **OpenRouter** (um agregador cobre imagem, vídeo e LLM); fal e ElevenLabs
são opcionais. Lista e motivos: `<plugin-root>/references/provedores.md`.

Para cada chave que a pessoa quiser guardar, peça para ela mesma rodar (entrada escondida):

- Claude Code: `! pwdev-media chaves guardar openrouter`
- Codex e Hermes: `pwdev-media chaves guardar openrouter` no terminal dela

Fora do macOS a CLI explica como definir a variável de ambiente. Depois, confira com
`pwdev-media status --ao-vivo` e diga só "ok" ou o erro do provedor.

## 4. Orçamento (opcional)

Pergunte uma vez se ela quer um teto mensal. Se sim: `pwdev-media custo orcamento <valor-em-usd>`.

## 5. Fechamento

Uma linha com o que ficou pronto e o próximo passo natural: ver modelos
(`media-catalogo`) ou gerar algo (`media-gerar`), na forma de comando do runtime atual.
