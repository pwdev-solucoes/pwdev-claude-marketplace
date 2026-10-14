---
name: vhf-cenas
description: >
  Use quando um momento do vídeo pedir uma animação sob medida que texto simples não resolve —
  'anima esse número', 'mostra a lista com check', 'faz um gráfico subindo', 'antes e depois',
  'passo a passo animado', 'cartão de preço', 'diagrama que cresce'. Escreve uma sub-composição
  HyperFrames para aquela fala com as skills oficiais e a encaixa no projeto.json, entrando na
  palavra. Não use para textos simples (vhf-plano) nem para gerar imagem ou vídeo por IA
  (media-gerar).
metadata:
  version: 0.1.0
---

# Cenas sob medida

Regras: `<plugin-root>/references/regras.md` e `<plugin-root>/templates/projeto-hf/compositions/LEIA.md`.

## 1. Antes de escrever

- Carregue as skills oficiais `hyperframes-core` e `hyperframes-animation` (instaladas pelo
  `vhf-setup`); para gráficos sobre a fala, veja também `talking-head-recut`.
- Confirme o material: todo número, nome e item vem da fala (`pwdev-media video fala '<EDIT>'`) ou
  de um arquivo da pessoa. Faltou: pergunte, não invente.
- Pegue os tempos das palavras em `<EDIT>/cut_timeline.json` (tempos no corte).

## 2. Escrever a cena

`<PROJ>/compositions/<nome>.html`, com `data-composition-id` único, as mesmas dimensões do projeto
(`pwdev-media formatos mostrar <formato>`), timeline pausada em `window.__timelines["<id>"]` e só
lógica determinística.

- O tempo da cena começa em 0 no `inicio` dela: cada item entra em `palavra.inicio - cena.inicio`.
- Sobre a pessoa: fundo transparente, peça acima da cabeça, dentro da zona segura.
- Tela cheia sem a pessoa: no máximo uma a cada 15–20 s.
- Fonte: `assets/fonts/Montserrat.ttf` com `@font-face` (o HyperFrames só usa fonte em arquivo).

## 3. Encaixar e conferir

```json
"cenas": [{"inicio": 12.4, "fim": 15.8, "src": "compositions/<nome>.html", "sobre_a_pessoa": true}]
```

Nenhum texto do `projeto.json` pode estar na tela ao mesmo tempo.

```bash
python3 '<PROJ>/build.py' amostra <inicio - 2> <fim + 2>
python3 '<PROJ>/build.py' hf check
python3 '<PROJ>/build.py' hf snapshot
```

Olhe os quadros: lê-se no tamanho do celular? Cobre o rosto? Entra na palavra? Ajuste e repita.
Cada cena com movimento ganha um efeito sonoro casado (`vhf-som`).
