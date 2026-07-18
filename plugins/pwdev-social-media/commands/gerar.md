---
description: Gera ativo por IA — triagem, prompt, confirmação de custo, geração e curadoria
argument-hint: "[descrição do ativo]"
---

# /pwdev-social-media:gerar — Gerar ativo

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Triagem: precisa mesmo gerar?

| Pergunta | Se sim |
|---|---|
| É texto sobre fundo liso? | **não gere** — composição |
| Já existe no acervo? | **não gere** — use |
| Existe vetor no design system? | **não gere** — use |
| Dá para fotografar? | avalie: foto real costuma sair melhor e mais barata |
| É fundo, textura ou cena inexistente? | gere |

Se a resposta for "não gere", **diga isso** e proponha o caminho de composição.
É a etapa que mais economiza orçamento.

## STEP 2 — Ferramenta
| Necessidade | Ferramenta | Variável |
|---|---|---|
| **Texto legível na arte** | Ideogram | `IDEOGRAM_API_KEY` |
| Ilustração repetível | Leonardo | `LEONARDO_API_KEY` |
| Fotorrealismo | Flux | `BFL_API_KEY` |
| Vídeo a partir de imagem | Runway | `RUNWAY_API_KEY` |
| Upscale | Freepik/Magnific | `FREEPIK_API_KEY` |

Verifique com `${CLAUDE_PLUGIN_ROOT}/scripts/check-keys.sh`.
Sem chave: modo prompt — prompt otimizado, **nada gerado**.

## STEP 3 — Prompt
`prompt-craft` + bloco base de `visual-consistency`.
Campanha em andamento: reutilize modelo e bloco base fixados.

## STEP 4 — Confirmar custo
Declare ferramenta, quantas variações e chamadas previstas.
**Espere confirmação explícita.** Vídeo confirma separado.

## STEP 5 — Gerar
Spawn do `asset-generator`. **2 variações na primeira rodada, nunca 8.**

## STEP 6 — Curar
`asset-curation`. Grade como Artifact. **Registre a seed.**

Nenhuma variação serve: volte ao STEP 3, ajuste **um eixo**, gere 2.
Após 3 rodadas, pare e reavalie se o caminho é geração.
