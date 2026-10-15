---
name: vtut-revisar
description: >
  Use quando for revisar, renderizar e entregar um vídeo tutorial de sistema — 'renderiza o
  tutorial', 'confere antes de publicar', 'a narração está fora do clique', 'aparece um e-mail de
  verdade', 'a tela mudou, regrava'. Confere sincronia entre fala e ação, mascaramento, capítulos e
  legenda, renderiza com o portão de qualidade no perfil de tutorial e atualiza o roadmap. Não use
  para escrever roteiro (vtut-roteiro) nem para montar (vtut-montar).
metadata:
  version: 0.1.0
---

# Revisão e entrega

Runtime: `<plugin-root>/references/runtime.md`. Roteiro e regras: `<plugin-root>/references/roteiro.md`.

## 1. Conferências

```bash
python3 '<plugin-root>/scripts/tutorial.py' conferir '<V>' --roteiro '<V>/roteiro.json'
```

| Achado | Conserto |
|---|---|
| narração passa do fim da cena | cena curta demais: some uma `esperar` ou divida a fala; regrave |
| tela parada > 3 s sem fala | divida a narração da cena para acompanhar as ações |
| dado pessoal sem máscara | ponha o seletor em `mascarar` ou use dado fictício; regrave |
| cenas não batem com o roteiro | o roteiro mudou depois da gravação: regrave |

Olhe as capturas e o estúdio com som: a fala bate com o clique? O nome do botão dito é o da tela?
Algum dado real aparece (nome de cliente, e-mail, CPF, saldo)? Se aparecer, regrave com máscara —
borrar depois não é aceitável.

## 2. Render (~1–3× a duração)

```bash
python3 '<V>/projeto-hf/build.py' completo
python3 '<V>/projeto-hf/build.py' render --qualidade high --max-silencio 5
```

Em tutorial a tela pode ficar uns segundos sem fala enquanto carrega: o portão aceita até 5 s
(`--max-silencio 5`) e reprova o resto (estouro de áudio, legenda faltando palavra). Só entregue
com **PASSOU**.

## 3. Entrega

Até 5 linhas: arquivo do vídeo, `tutorial.md`, duração, voz usada, o que foi mascarado. Atualize o
`status` do vídeo para `gravado` no `roadmap.json` e diga qual é o próximo da ordem de produção.
Apague `<TUT>/sessao.json` quando a série terminar (ou peça para a pessoa apagar).
