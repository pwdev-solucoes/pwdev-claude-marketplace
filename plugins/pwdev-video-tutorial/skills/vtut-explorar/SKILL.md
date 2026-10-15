---
name: vtut-explorar
description: >
  Use quando a pessoa quiser que a IA conheça um sistema antes de fazer vídeos dele — 'explora o
  sistema', 'mapeia as telas', 'lê o código e navega no sistema', 'quais funcionalidades existem',
  'o que dá para ensinar desse sistema'. Varre o código (rotas, menus, formulários, permissões),
  navega no sistema real com o playwright-cli (com login feito pela pessoa), compara as duas fontes
  e escreve o mapa do sistema com capturas e lacunas. Não use para planejar a série de vídeos
  (vtut-roadmap) nem para escrever um roteiro (vtut-roteiro).
metadata:
  version: 0.1.0
---

# Explorar o sistema (código + navegação)

Guia completo: `<plugin-root>/references/exploracao.md`. Runtime e pastas:
`<plugin-root>/references/runtime.md`.

## 0. Combinar

Pergunte, numa mensagem só: o endereço do sistema (homologação de preferência), se há login, a
pasta do código (opcional, mas melhora muito) e para quem são os vídeos. Crie `<TUT>` e, se for
dentro de um repositório, ponha `.pwdev-tutorial/` no `.gitignore` (guarda a sessão de login).

## 1. Código (se houver)

```bash
python3 '<plugin-root>/scripts/tutorial.py' codigo '<raiz>' --saida '<TUT>/codigo.json'
```

Leia o resumo e abra só os arquivos que explicam os fluxos principais (rota → controller/página →
validação → mensagem). Anote arquivo:linha.

## 2. Navegação

Login feito pela pessoa numa janela visível; depois salve a sessão (`state-save`). Percorra os
menus e as rotas de tela do código, com snapshot e captura por tela, e guarde as URLs em
`<TUT>/visitadas.txt`. Sem enviar formulário fora de ambiente de teste.

```bash
python3 '<plugin-root>/scripts/tutorial.py' cobertura '<TUT>/codigo.json' --visitadas '<TUT>/visitadas.txt'
```

## 3. Mapa

Escreva `<TUT>/mapa-do-sistema.md` (seções em `<plugin-root>/references/exploracao.md`): perfis,
telas, fluxos, campos sensíveis, lacunas, fontes. Mostre à pessoa um resumo de até 8 linhas e 2 ou 3
capturas, com as lacunas como perguntas. Próximo passo: `vtut-roadmap`.

Feche a sessão do navegador ao terminar (`playwright-cli -s=pwdev-tutorial close`).
