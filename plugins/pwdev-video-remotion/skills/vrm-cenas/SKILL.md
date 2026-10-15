---
name: vrm-cenas
description: >
  Use quando um momento do vídeo em Remotion pedir uma animação sob medida que texto simples não
  resolve — 'anima esse número', 'mostra a lista com check', 'faz um gráfico subindo', 'antes e
  depois', 'passo a passo animado', 'cartão de preço', 'diagrama que cresce'. Escreve um componente
  React para aquela fala com as skills oficiais do Remotion e o encaixa no projeto.json, entrando na
  palavra. Não use para textos simples (vrm-plano) nem para gerar imagem ou vídeo por IA
  (media-gerar).
metadata:
  version: 0.2.0
---

# Cenas sob medida em React

Regras: `<plugin-root>/references/regras.md` e
`<plugin-root>/templates/projeto-remotion/compositions/LEIA.md`.

## 1. Antes de escrever

- Carregue as skills oficiais do Remotion (instaladas pelo `vrm-setup`) para animação, `spring` e
  `interpolate`.
- Confirme o material: todo número, nome e item vem da fala (`pwdev-media video fala '<EDIT>'`) ou
  de um arquivo da pessoa. Faltou: pergunte, não invente.
- Pegue os tempos das palavras em `<EDIT>/cut_timeline.json` (tempos no corte).

## 2. Escrever a cena

Copie `<PROJ>/compositions/exemplo-contador.tsx` para `<PROJ>/compositions/<nome>.tsx` e adapte:

- `export default` de um `React.FC<CenaProps>` (`src/tipos.ts`);
- tudo animado por `useCurrentFrame()`; o tempo começa em 0 no `inicio` da cena, então cada item
  entra em `palavra.inicio - cena.inicio`;
- tamanhos × `unidade`; posição dentro de `zonaSegura`; com `sobreAPessoa`, peça acima da cabeça;
- nada de `Date.now()`, `Math.random()`, `setTimeout`, CSS transition ou fetch.

## 3. Encaixar e conferir

```json
"cenas": [{"inicio": 12.4, "fim": 15.8, "src": "compositions/<nome>.tsx", "sobre_a_pessoa": true}]
```

Nenhum texto do `projeto.json` pode estar na tela ao mesmo tempo.

```bash
python3 '<PROJ>/build.py' amostra <inicio - 2> <fim + 2>
python3 '<PROJ>/build.py' checar
python3 '<PROJ>/build.py' quadro <segundo no meio da cena, contado a partir do início da amostra>
```

Olhe o quadro: lê-se no tamanho do celular? Cobre o rosto? Entra na palavra? Ajuste e repita. Cada
cena com movimento ganha um efeito sonoro casado (`vrm-som`).

Uma cena `.tsx` só roda no Remotion. Se a pessoa trocar para o HyperFrames, a cena precisa ser
reescrita em HTML (o resto do `projeto.json` serve igual).
