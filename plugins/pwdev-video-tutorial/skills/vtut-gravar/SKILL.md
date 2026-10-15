---
name: vtut-gravar
description: >
  Use quando for gravar a tela de um vídeo tutorial a partir do roteiro — 'grava o tutorial',
  'grava a tela', 'regrava porque a tela mudou', 'faz a captura do fluxo'. Executa o roteiro no
  sistema real pelo playwright-cli, com capítulos, contorno e nota nos cliques, digitação humana,
  campos sensíveis borrados e cada cena segurada pelo tempo da narração; mede o tempo de cada ação
  e salva uma captura por cena. Não use para escrever o roteiro (vtut-roteiro) nem para montar o
  vídeo final (vtut-montar).
metadata:
  version: 0.1.0
---

# Gravação da tela

Runtime e sessão: `<plugin-root>/references/runtime.md`. Formato das ações:
`<plugin-root>/references/roteiro.md`.

## 1. Antes

- Roteiro aprovado e válido; narração pronta (`<V>/narracao.json`). Sem narração, a gravação usa só
  as pausas das ações (dá para narrar depois, mas aí a fala pode não caber na cena).
- Ambiente de teste com os dados fictícios que o roteiro usa (o cliente "Maria Exemplo" precisa
  poder ser criado). Em produção, só com o "sim" da pessoa e sem salvar nada.
- Sistema com login: sessão salva em `<TUT>/sessao.json` (`vtut-explorar`).

## 2. Gravar (~ a duração do vídeo + 10 s)

```bash
python3 '<plugin-root>/scripts/tutorial.py' gravar '<V>/roteiro.json' --pasta '<V>' [--estado '<TUT>/sessao.json']
```

Sai `<V>/gravacao.webm`, `<V>/cenas.json` (tempo de cada ação e caixa de cada elemento clicado) e
`<V>/capturas/<cena>.png`. Para ver o script antes: `tutorial.py script ...` gera `<V>/gravar.js`.

Falhou numa ação: o localizador mudou ou a tela demorou. Abra a tela com o playwright-cli, corrija o
`alvo` (ou ponha `{"tipo": "esperar", "valor": 1500}` antes) e grave de novo.

## 3. Conferir

```bash
python3 '<plugin-root>/scripts/tutorial.py' conferir '<V>' --roteiro '<V>/roteiro.json'
```

Olhe 2 ou 3 capturas: o campo sensível está borrado? A tela certa aparece? Avisos de "tela sem
fala" pedem dividir a narração da cena. Próximo: `vtut-montar`.
