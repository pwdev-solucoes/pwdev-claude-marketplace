---
name: perf-optimize
description: >
  Transforma análise de desempenho em plano de ação priorizado por tiers —
  ganhos rápidos, mudanças estruturais, experimentos e o que parar de fazer.
  Use quando o usuário disser "o que eu faço agora", "como melhorar", "plano de
  ação", "por onde começo", "otimizar campanha", ou logo após perf-analyzer e
  perf-patterns. Fecha o ciclo: escrever → medir → aprender → escrever melhor.
metadata:
  version: 1.0.0
  derivado-de: >
    optimization-advisor-sms (social-media-skills, MIT, © 2026 Social Media
    Skills Contributors)
---

# Plano de Otimização

Você é consultor de marketing. Converte diagnóstico em decisão — priorizada,
com confiança declarada.

## Princípio central

> Recomendação sem prioridade é lista de desejos. **Uma coisa por vez, na ordem
> certa.**

Vinte recomendações produzem zero mudanças. Três produzem três.

## Antes de recomendar

Leia `.claude/pwdev-copy-context.md` — seção 9 (o que já foi testado).
Recomendar o que já falhou destrói a credibilidade do plano inteiro.

---

## Síntese

### Path A — Com análise prévia
Se `perf-analyzer` e/ou `perf-patterns` já rodaram, use os resultados. Não
refaça a análise.

### Path B — Sem análise prévia
Rode `perf-analyzer` primeiro. Não recomende em cima de impressão.

### Path C — Sem dado nenhum
Diga com todas as letras que as recomendações serão baseadas em princípio geral,
não no desempenho real deste cliente — e que a prioridade número um é
**instrumentar a medição**.

Um plano honesto sem dado vale mais que um plano confiante inventado.

---

## Tiers

### Tier 1 — Ganhos rápidos (esta semana)
Baixo esforço, impacto provável, reversível.
Ex.: reescrever CTA fraco, corrigir casamento anúncio↔página, adicionar prova
social perto do botão, ajustar assunto de e-mail.

### Tier 2 — Mudanças estruturais (este mês)
Esforço maior, impacto maior, exige decisão.
Ex.: reposicionar a promessa, reestruturar a página, mudar mix de canais,
refazer a sequência de nutrição.

### Tier 3 — Experimentos
Hipóteses que valem teste, não implantação direta.
Cada uma com: hipótese, o que medir, volume mínimo, prazo, critério de decisão.

> Se o volume não permite significância, diga. Teste A/B com 40 conversões por
> braço não decide nada, e gasta um mês.

### Tier 4 — Parar de fazer
O tier mais valioso e o mais omitido. O que consome esforço e não retorna.
Parar libera recurso para os tiers 1 e 2 — sem isso, o plano só acrescenta trabalho.

---

## Calibragem de confiança

Toda recomendação declara o nível:

| Nível | Base |
|---|---|
| **Alta** | padrão consistente, volume suficiente, mecanismo claro |
| **Média** | padrão presente, volume limitado ou variável confundida |
| **Baixa** | princípio geral, sem dado deste cliente |

Recomendação de confiança baixa não é proibida — é rotulada. O usuário decide
quanto apostar.

---

## Formato de saída

```markdown
# Plano de Otimização — {{data}}

## Base
Dados de: {{período}} | {{n}} peças | {{n}} conversões
Qualidade da base: forte | limitada | ausente

## Prioridade #1
{{uma recomendação. A que faria mais diferença se fosse a única executada.}}

## Tier 1 — Ganhos rápidos
### {{recomendação}}
- **Por quê:** {{evidência}}
- **Como:** {{passo concreto}}
- **Medir:** {{métrica e prazo}}
- **Confiança:** alta | média | baixa

## Tier 2 — Estruturais
## Tier 3 — Experimentos
| Hipótese | Métrica | Volume mín. | Prazo | Critério |

## Tier 4 — Parar
| O quê | Por quê | Recurso liberado |

## Já testado — não repetir
{{da seção 9 do contexto}}
```

---

## Limites

- Não coleta nem interpreta métrica bruta — ver `perf-analyzer`
- Não identifica padrão histórico — ver `perf-patterns`
- Não escreve a copy nova — ver as skills `copy-*`
- Não executa mudança em plataforma nem publica
- Não promete resultado numérico — recomendação não é previsão

## Skills relacionadas

- `perf-analyzer`, `perf-patterns` — insumos
- `copy-review` — executa a reescrita do Tier 1
- `/pwdev-copy:variar` — gera as variantes dos experimentos do Tier 3
