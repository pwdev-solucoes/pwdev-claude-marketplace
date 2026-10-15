---
name: vtut-roteiro
description: >
  Use quando for escrever o roteiro de um vídeo tutorial, explicativo ou de novidade de um sistema
  — 'escreve o roteiro do vídeo de cadastro', 'roteiro do tutorial', 'como explicar essa
  funcionalidade', 'storytelling do vídeo', 'próximo vídeo do roadmap'. Aplica a estrutura gancho →
  contexto → demonstração → resultado → próximo passo, escreve a narração e as ações de tela com
  localizadores verificados no sistema real, marca dados sensíveis e valida. Não use para planejar a
  série (vtut-roadmap) nem para gravar (vtut-gravar).
metadata:
  version: 0.1.0
---

# Roteiro com storytelling

Estrutura, regras de narração e formato: `<plugin-root>/references/roteiro.md`.

## 1. Material

O vídeo do `roadmap.json` (objetivo, público, rotas, pré-requisitos), o mapa do sistema e as
capturas. Abra o fluxo no sistema com o playwright-cli e **confirme cada localizador** que vai usar
(`snapshot`, `generate-locator`). Nada de passo que você não executou.

## 2. Escrever

`<V>/roteiro.json` com uma cena por passo visível:

- gancho com o resultado ("em 1 minuto você…"), contexto e pré-requisito;
- demonstração: a fala diz a ação **enquanto** ela acontece, com o nome exato do botão;
- resultado visível (mensagem de sucesso, item na lista) e próximo passo (próximo vídeo da série);
- `mascarar` com o seletor CSS de todo campo sensível que aparecer; valores digitados fictícios
  (`"ficticio": true`);
- duração somada perto da `duracao_alvo_s` (≈ 2,8 palavras por segundo de fala).

```bash
python3 '<plugin-root>/scripts/tutorial.py' validar '<V>/roteiro.json'
```

## 3. Aprovar

`<V>/roteiro.md`: tabela cena · fala · o que aparece na tela · segundos. Mostre e espere o "sim"
(ou ajuste). Atualize o `status` do vídeo para `roteiro` no `roadmap.json`. Próximo: `vtut-narrar`.
