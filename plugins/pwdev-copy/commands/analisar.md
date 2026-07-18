---
description: Fecha o ciclo — analisa desempenho da copy, identifica padrões e entrega plano de otimização priorizado
argument-hint: "[período ou arquivo de métricas]"
---

# /pwdev-copy:analisar — Analisar e otimizar

Este comando fecha o ciclo do framework: **escrever → medir → aprender → escrever melhor**.

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Base de dados
Colete o que existir (Path B é o padrão hoje — não há MCP de analytics conectado):
- período
- peças publicadas, com canal e formato
- métricas por peça
- baseline (seção 9 do contexto)

Se não houver baseline **nem** período anterior, avise: a análise será
descritiva, não comparativa.

## STEP 2 — Portão de volume
| Situação | Ação |
|---|---|
| < 10 peças | rode só `perf-analyzer`; padrão não é possível |
| 10-20 peças | `perf-analyzer` + `perf-patterns` marcado como preliminar |
| > 20 peças | os três, análise completa |

Não force `perf-patterns` com volume insuficiente. Padrão inventado guia meses
de conteúdo na direção errada.

## STEP 3 — Executar em ordem
1. `perf-analyzer` — o que aconteceu
2. `perf-patterns` — o que se repete
3. `perf-optimize` — o que fazer

Cada um consome a saída do anterior. Não pule etapa.

## STEP 4 — Persistir o aprendizado
Atualize a **seção 9** de `.claude/pwdev-copy-context.md` com o que foi testado
e o resultado. É isso que impede o plugin de recomendar de novo o que já falhou.

Pergunte antes de gravar.

## STEP 5 — Entregar
Plano priorizado, com a prioridade #1 destacada e a qualidade da base declarada.
