---
name: social-upscale
description: >
  Use quando a imagem estiver pequena ou pixelada — 'upscale', 'melhorar a resolução',
  'imagem pixelada', 'Magnific', 'Freepik', 'aumentar a imagem'. Diagnostica antes (upscale não
  conserta foco nem logo raster) e, com chave e o "sim", amplia pelo Magnific via `pwdev-media
  gerar`, sem nunca sobrescrever o original. Não use para gerar imagem nova (social-imagem).
metadata:
  version: 3.0.0
---

# Upscale de Ativo

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma:
`<plugin-root>/references/language.md`.

Você recupera resolução. Antes disso, verifica se o problema é mesmo resolução.

## Princípio central

> Upscale **não recupera informação que não existe**. Recupera nitidez e tamanho — não conserta foto
> desfocada, mal enquadrada ou de baixa qualidade.

## Antes de gastar crédito

| Sintoma | Causa provável | Upscale resolve? |
|---|---|---|
| Serrilhado ao ampliar | resolução baixa | **sim** |
| Borrado uniforme | foco errado na captura | não |
| Blocos e artefatos | compressão JPEG agressiva | parcialmente |
| Ruído em foto escura | ISO alto | parcialmente |
| Logo pixelado | usaram raster em vez de vetor | **não — busque o SVG** |

Logo pixelado é o caso mais comum e o mais desnecessário. Antes de fazer upscale de logo, procure o
vetor no brand kit. Sempre existe.

> Antes de qualquer upscale, pergunte: existe o arquivo original em resolução maior? Na maioria das
> vezes existe, e o upscale era desnecessário.

## Com chave — Magnific

```bash
pwdev-media gerar magnific:upscale --arquivo '{{imagem.png}}' --escala 2x \
  --saida '.pwdev-social/gerados/{{AAAA-MM-DD}}-upscale' --estimar
```

Mostre o que vai processar e a estimativa, **espere o "sim"** e repita com `--confirmar`. Escalas:
`2x`, `4x`, `8x`, `16x` (o resultado não passa de ~25 megapixels). A saída vai para a pasta de
gerados; **o original nunca é sobrescrito**. Chave: `pwdev-media chaves guardar magnific` (a variável
antiga `FREEPIK_API_KEY` continua aceita).

## Sem chave

Oriente o processo manual na interface e diga que nada foi processado. Alternativas sem custo:
exportar de novo do Figma na escala correta (**sempre a melhor opção quando a origem é vetorial**) ou
reexportar do arquivo original em resolução maior.

## Formato de saída

```
Origem: {{arquivo}} — {{dimensão}}
Diagnóstico: {{causa}} — upscale resolve: sim | parcialmente | não
Processado: {{arquivo}} — {{dimensão}} — fator {{n}}×
Custo: {{informado pelo provedor}}
```

Quando o diagnóstico for "não", **diga isso antes de processar** e proponha o caminho certo.

## Limites

- Não gera imagem nova — ver `social-imagem`
- Não corrige foco, enquadramento nem exposição
- Não sobrescreve o original
- Não gasta crédito sem confirmação

## Skills relacionadas

- `social-imagem` — origem dos ativos gerados
- `social-entrega` — export em escala correta costuma dispensar upscale
