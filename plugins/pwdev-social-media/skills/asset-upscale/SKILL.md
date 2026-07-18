---
name: asset-upscale
description: >
  Aumenta resolução e qualidade de imagem via Freepik/Magnific, ou orienta o
  processo manual quando não há chave. Use quando o usuário disser "upscale",
  "melhorar a resolução", "a imagem está pixelada", "Magnific", "Freepik",
  "aumentar a imagem", "imagem pequena demais". Gasta crédito — exige
  confirmação.
metadata:
  version: 1.0.0
---

# Upscale de Ativo

Você recupera resolução. Antes disso, verifica se o problema é mesmo resolução.

## Princípio central

> Upscale **não recupera informação que não existe**. Recupera nitidez e
> tamanho — não conserta foto desfocada, mal enquadrada ou de baixa qualidade.

## Antes de gastar crédito

Diagnostique. Muita gente pede upscale para problema que não é resolução:

| Sintoma | Causa provável | Upscale resolve? |
|---|---|---|
| Serrilhado ao ampliar | resolução baixa | **sim** |
| Borrado uniforme | foco errado na captura | não |
| Blocos e artefatos | compressão JPEG agressiva | parcialmente |
| Ruído em foto escura | ISO alto | parcialmente |
| Logo pixelado | usaram raster em vez de vetor | **não — busque o SVG** |

Logo pixelado é o caso mais comum e o mais desnecessário. Antes de fazer upscale
de logo, procure o vetor no brand kit. Sempre existe.

## Portão de custo

Igual a `image-gen`: diga o que vai processar, estime o custo, **espere
confirmação**, só então execute.

## Path A — Chave configurada
`FREEPIK_API_KEY` via `Bash` + `curl`. Nunca peça, escreva ou imprima a chave.

Salve como `{{original}}_up{{fator}}.png`, preservando o original.
**Nunca sobrescreva o arquivo de origem.**

## Path B — Sem chave
Oriente o processo manual na interface e diga que nada foi processado.

Alternativas locais que resolvem casos simples sem custo: exportar de novo do
Figma na escala correta (**sempre a melhor opção quando a origem é vetorial**),
ou reexportar do arquivo original em resolução maior.

> Antes de qualquer upscale, pergunte: existe o arquivo original em resolução
> maior? Na maioria das vezes existe, e o upscale era desnecessário.

## Formato de saída

```
Origem: {{arquivo}} — {{dimensão}}
Diagnóstico: {{causa}} — upscale resolve: sim | parcialmente | não
Processado: {{arquivo}} — {{dimensão}} — fator {{n}}×
Custo: {{estimado}}
```

Quando o diagnóstico for "não", **diga isso antes de processar** e proponha o
caminho certo.

## Limites

- Não gera imagem nova — ver `image-gen`
- Não corrige foco, enquadramento nem exposição
- Não sobrescreve o original
- Não gasta crédito sem confirmação

## Skills relacionadas

- `image-gen` — origem dos ativos gerados
- `export-handoff` — export em escala correta costuma dispensar upscale
