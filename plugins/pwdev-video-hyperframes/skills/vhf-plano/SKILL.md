---
name: vhf-plano
description: >
  Use quando for decidir o que aparece na tela em cada momento de um vídeo já cortado — 'monta o
  plano', 'onde entra o texto', 'deixa mais dinâmico', 'põe zoom', 'o que mostrar quando falo do
  preço', 'muda o ritmo'. Divide a fala por ideia e escreve blocos de enquadramento e textos no
  projeto.json, cada um entrando na palavra certa. Não use para cortar (vhf-corte) nem para criar
  uma animação sob medida (vhf-cenas).
metadata:
  version: 0.1.0
---

# Plano em blocos

Regras: `<plugin-root>/references/regras.md`. Campos: `<plugin-root>/references/projeto.md`.
Receitas: `<plugin-root>/references/modelos.md`.

## 1. Ler a fala do corte

```bash
pwdev-media --json video fala '<EDIT>'
```

Para o tempo de cada palavra, leia `palavras` em `<EDIT>/cut_timeline.json` (tempos no corte).

## 2. Dividir por ideia

Tabela curta para você (e para a pessoa, se ela pediu para aprovar o plano): bloco, trecho da fala,
o que aparece, o que continua no próximo.

| Tipo de fala | Peça |
|---|---|
| gancho, promessa | `titulo` no topo nos 2 primeiros segundos |
| nome de passo, tópico, pergunta | `rotulo` |
| número, lista, passos, comparação, prova | cena sob medida (`vhf-cenas`) |
| ênfase, virada | zoom 1.12–1.3 no bloco |
| chamada falada | `rotulo` na base |

Ritmo: algo muda a cada 2 a 4 s; uma ideia por vez; a pessoa fica na tela.

## 3. Escrever no projeto.json

- `blocos`: um por frase ou grupo de frases, alternando `zoom` 1.0 e ~1.12, e 1.25–1.3 nas
  palavras de ênfase (pelo menos 2,5 s entre aproximações).
- `textos`: `inicio` no tempo da palavra que chama (até 0,15 s antes), `fim` quando a ideia acaba,
  texto curto (até 6 palavras), escrito como a pessoa falou.

```bash
pwdev-media video projeto '<PROJ>/projeto.json'
python3 '<PROJ>/build.py' montar
```

O validador reprova sobreposição e tempos fora do corte; corrija até passar.
