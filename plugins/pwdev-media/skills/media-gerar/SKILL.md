---
name: media-gerar
description: >
  Use quando a pessoa pedir para gerar imagem, vídeo, trilha, efeito sonoro ou narração com IA
  por um provedor (OpenRouter, fal, ElevenLabs) — 'gera uma imagem de produto', 'cria um clipe de
  5 s em 9:16', 'faz uma trilha animada de 30 s', 'um efeito de whoosh', 'narra esse texto'.
  Escolhe o item no catálogo, mostra a estimativa, pede o ok, gera, registra o custo e lembra o
  rótulo de IA. Não use para escolher entre modelos sem gerar (media-catalogo) nem para editar um
  vídeo gravado (plugins pwdev-video-*).
metadata:
  version: 0.5.0
---

# Gerar mídia com custo controlado

Runtime, CLI e segredos: `<plugin-root>/references/runtime.md`. Provedores e códigos de saída:
`<plugin-root>/references/provedores.md`.

## 1. Escolher o item

Se a pessoa não disse o modelo, use `pwdev-media catalogo recomendar --categoria <id> --so-com-chave`
e escolha o primeiro que tem `modelo` preenchido. Diga em uma linha qual e por quê.

## 2. Montar o pedido

- Prompt em inglês quando o modelo rende melhor assim; mostre a versão em pt-BR para a pessoa.
- Formato: confira `media-formatos` (proporção e resolução do destino) e os `limites` do item.
- Fidelidade: nada de marca, pessoa real, número ou prova que a pessoa não forneceu.

## 3. Estimar e pedir o ok

```bash
pwdev-media gerar <item> --prompt '<texto>' [--duration 5 --aspect-ratio 9:16 --resolution 720p] --estimar
```

Mostre: item, quantidade, valor estimado e a data do preço. **Pare e espere o "sim"** explícito
nesta conversa. Preço desconhecido: diga que o provedor informa o custo real depois.
Texto com `$` ou aspas vai entre aspas simples (ver `<plugin-root>/references/runtime.md`).

## 4. Gerar

```bash
pwdev-media gerar <item> --prompt '<texto>' [...] --confirmar [--saida '<pasta>']
```

- Código 4 (orçamento): avise e só repita com `--acima-do-orcamento` se ela confirmar.
- Código 6 (sem chave): leve para `media-setup`.
- Código 5 (provedor): mostre a mensagem; nunca tente outro formato de API por conta própria.
- Mesmo pedido já gerado e ainda no disco: a CLI reaproveita, sem custo.

Vídeo demora de 1 a 5 minutos: avise antes.

## 5. Entregar

Caminho do arquivo, custo informado pelo provedor e, quando a CLI lembrar, que o conteúdo deve ser
marcado como gerado por IA ao publicar. Licença comercial diferente de `sim`: repita o aviso.
Mostre a imagem ou um quadro do vídeo quando o runtime permitir.
