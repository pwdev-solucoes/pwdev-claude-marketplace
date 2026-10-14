---
name: media-catalogo
description: >
  Use quando a pessoa perguntar qual modelo ou aplicativo de IA usar para uma tarefa de mídia, ou
  quiser consultar o catálogo — 'qual o modelo de vídeo mais barato', 'melhor upscale de vídeo',
  'o que usar para limpar a voz', 'alternativa ao Runway', 'quanto custa gerar 5 s no Kling',
  'mostra o catálogo de trilha', 'posso usar essa música em anúncio?'. Consulta e recomenda por
  categoria, objetivo (barato, equilibrado, máximo), preço, qualidade e licença comercial. Não use
  para atualizar preços (media-atualizar) nem para gerar (media-gerar).
metadata:
  version: 0.1.0
---

# Consultar e recomendar no catálogo

Runtime e CLI: `<plugin-root>/references/runtime.md` (comece por `pwdev-media versao`). Campos,
categorias e regras: `<plugin-root>/references/catalogo.md`.

## 1. Entender o pedido

Mapeie para uma categoria (`pwdev-media catalogo categorias`) e um objetivo:

- "barato", "economizar", "teste" → `barato`;
- "melhor", "máxima qualidade", "anúncio grande" → `maximo`;
- sem pista → `equilibrado`.

## 2. Consultar

```bash
pwdev-media catalogo recomendar --categoria <id> --objetivo <objetivo>
pwdev-media catalogo listar --categoria <id>          # visão completa, inclusive sem nota
pwdev-media catalogo mostrar <id-do-item> --json      # detalhes de um item
```

Use `--so-com-chave` quando a pessoa quer algo que já funcione com as chaves dela.

## 3. Responder

Tabela curta (até 5 linhas): item, via (agregador, API, assinatura, local), preço com unidade e
data da verificação, qualidade, licença comercial. Depois **uma** recomendação com o motivo.

Avise sempre que:

- o preço tem mais de 30 dias ou veio de fonte de terceiros (está em `notas`): sugira
  `media-atualizar`;
- a licença comercial é `a_verificar` ou `nao` e o uso é anúncio;
- o item não tem `modelo` (slug) e por isso ainda não gera pelo `pwdev-media`;
- é assinatura sem API: o uso é no app do provedor, fora da automação.

Nunca invente preço, modelo ou licença que não estão no catálogo. Faltou: diga que não está no
catálogo e ofereça rodar a atualização ou registrar o item na curadoria.
