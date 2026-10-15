---
name: vrm-corte
description: >
  Use quando a pessoa quiser só o corte de um vídeo falado, ou ajustar o corte — 'tira as pausas',
  'corta os erros', 'fica com a última tomada', 'junta essas gravações', 'volta a frase X', 'tirou
  uma palavra', 'cortou o fim da palavra'. Transcreve localmente, separa frases e tomadas, monta o
  EDL, corta pela onda do áudio (sem respiros de 0,25 s ou mais) e confere. Não use para animação,
  legenda estilizada ou render final (vrm-editar, vrm-revisar).
metadata:
  version: 0.1.0
---

# Corte pela onda

Regras: `<plugin-root>/references/regras.md`. Ferramentas: `<plugin-root>/references/runtime.md`.

## 1. Fonte

Uma gravação: use o arquivo. Várias gravações do mesmo vídeo: junte numa fonte só, na ordem:

```bash
pwdev-media video juntar '<EDIT>/fonte.mp4' '<VIDEOS>/1.mov' '<VIDEOS>/2.mov'
```

## 2. Transcrever

Na primeira vez baixa o modelo de voz (~1,6 GB) e leva alguns minutos; avise. Depois, ~1/5 da
duração do vídeo.

```bash
pwdev-media video transcrever '<fonte>' --edit '<EDIT>' [--prompt 'Nome da Marca, Produto X']
```

Use `--prompt` com nomes difíceis que a pessoa citou. Vídeo só no iCloud trava a leitura: peça para
baixar (Finder > Baixar Agora).

## 3. Escolher as frases

Leia `<EDIT>/frases.md` (nunca o `transcricao.json` inteiro). Cada linha é uma frase com id e
tempo; `↺ F012` marca uma tomada refeita depois em F012.

- Padrão: `pwdev-media video montar '<EDIT>'` (todas as frases menos as tomadas refeitas).
- Ajuste quando a leitura mostrar: frase repetida que o automático não pegou, frase pela metade,
  "corta isso" dito na gravação, ordem que funciona melhor (anúncio: gancho, problema, virada, prova,
  chamada). Então: `pwdev-media video montar '<EDIT>' --frases F001,F004,F005`.

## 4. Cortar e conferir

```bash
pwdev-media video cortar '<EDIT>' [--qualidade rascunho]
pwdev-media video portao '<EDIT>/cut.mp4' --edit '<EDIT>'
pwdev-media video fala '<EDIT>'
```

- O portão tem de dizer **PASSOU** (sem respiro, sem estouro, legenda cobrindo toda palavra).
- Leia a `fala` do corte procurando palavra trocada ou nome escrito errado. Achou: grave em
  `<EDIT>/correcoes.json` (`{"errado": "certo"}`) e rode `pwdev-media video legendas '<EDIT>'`; ou
  transcreva de novo com `--prompt`.

## 5. Mostrar (se pediram para aprovar o corte)

Duração antes e depois, quantas frases saíram e por quê (uma linha), e o arquivo `cut.mp4` para
ouvir. Pedido "voltou a frase X" ou "cortou o fim de Y": ajuste o EDL e corte de novo.
