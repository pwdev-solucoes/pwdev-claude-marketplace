---
name: media-atualizar
description: >
  Use quando a pessoa quiser atualizar o catálogo de modelos e apps de mídia, ver o que mudou ou
  agendar a atualização — 'atualizar o catálogo', 'tem modelo novo de vídeo?', 'os preços
  mudaram?', 'agendar atualização mensal', 'o catálogo está velho'. Descobre modelos e preços por
  API (OpenRouter, npm), mescla sem tocar na curadoria, gera relatório de diferenças e lista o que
  precisa ser conferido à mão. Não use para recomendar um modelo (media-catalogo).
metadata:
  version: 0.2.0
---

# Atualizar o catálogo

Runtime e CLI: `<plugin-root>/references/runtime.md`. Regras de curadoria:
`<plugin-root>/references/catalogo.md`.

## 1. Rodar

```bash
pwdev-media catalogo atualizar
```

Leva menos de um minuto e não gasta nada (as fontes são públicas). O que faz:

- busca os modelos de vídeo e de imagem do OpenRouter, com preço por segundo e limites;
- busca a versão mais nova de `hyperframes` e `remotion` no npm (a versão fixa dos projetos
  **não** muda sozinha);
- mescla no `~/.pwdev/media/catalogo.json`: preço, limites e status mudam; nota de qualidade,
  licença e observações nunca mudam; o que sumiu vira `removido`;
- grava o relatório em `~/.pwdev/media/relatorios/AAAA-MM-DD.md`.

Fonte que falhar aparece no relatório e não apaga nada.

## 2. Resumir

Em até 6 linhas: quantos modelos novos, quais sumiram, preços que mudaram mais de 10%, motores
com versão nova e as assinaturas a conferir à mão (com o link). Não cole o relatório inteiro.

## 3. Curadoria (com a pessoa)

Para cada modelo novo relevante, ofereça dar a nota de qualidade e a licença **depois de testar**
(uma geração barata com `media-gerar`, com o ok dela). Edite `~/.pwdev/media/catalogo.json` e rode
`pwdev-media catalogo validar`. Nunca dê nota sem teste.

Motor com versão nova: diga que a troca da versão fixa é feita no plugin de vídeo, rodando os
testes de fumaça antes.

## 4. Agendar (opcional, só com o "sim")

```bash
pwdev-media catalogo agendar             # mostra o que seria instalado
pwdev-media catalogo agendar --instalar  # macOS: LaunchAgent no dia 1, 09:00
pwdev-media catalogo agendar --remover
```

No Claude Code também dá para usar uma rotina agendada da própria ferramenta, se a pessoa
preferir. Fora do macOS a CLI imprime a linha de cron ou do Agendador de Tarefas para ela adicionar.
